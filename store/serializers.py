
from django.db.transaction import atomic
from django.contrib.auth import get_user_model

from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers

from store.models import Cart, CartItem, Product, ProductImage, Review, UserProfile, Address
from store.paginations import ReviewPagination


User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='user.phone_number')

    class Meta:
        model = UserProfile
        fields = ["id", "first_name", "last_name", "username",
                  "email", "phone_number", "updated_at", "profile_avatar"]
        read_only_fields = ["phone_number"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["profile_avatar", "email", "first_name",
                  "last_name", "username", "updated_at",]
        read_only_fields = ["phone_number"]

    def update(self, instance, validated_data):
        for field in self.Meta.read_only_fields:
            validated_data.pop(field, None)

        for field, value in validated_data.items():
            if hasattr(instance, field) and field not in self.Meta.read_only_fields:
                setattr(instance, field, value)

        instance.save()
        return instance


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["address", "city", "province", "is_active"]

    def create(self, validated_data):
        try:
            user = self.context["request"].user
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            validated_data["user"] = user_profile

            with atomic():
                # If this new address should be active
                if validated_data.get("is_active", False):
                    # Set all existing addresses to inactive
                    updated_count = Address.objects.filter(
                        user=user_profile).update(is_active=False)
                    print(
                        f"Deactivated {updated_count} existing addresses for user {user.id}")

                # Create the new address
                address = Address.objects.create(**validated_data)
                print(f"Created new address {address.id} for user {user.id}")
                return address
        except Exception as e:
            print(f"Error creating address: {str(e)}")
            raise serializers.ValidationError(
                f"Failed to create address: {str(e)}")


class AddressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "address", "city", "province", "is_active"]
        read_only_fields = ["user"]

    def update(self, instance, validated_data):
        try:
            with atomic():
                for field in self.Meta.read_only_fields:
                    validated_data.pop(field, None)

                if validated_data.get("is_active", False):
                    updated_count = Address.objects.filter(
                        user=instance.user
                    ).exclude(
                        id=instance.id
                    ).update(is_active=False)
                    print(
                        f"Deactivated {updated_count} other addresses for user {instance.user.id}")

                for field, value in validated_data.items():
                    if hasattr(instance, field) and field not in self.Meta.read_only_fields:
                        setattr(instance, field, value)

                instance.save()
                print(
                    f"Updated address {instance.id} for user {instance.user.id}")
                return instance

        except Exception as e:
            print(f"Error updating address {instance.id}: {str(e)}")
            raise serializers.ValidationError(
                f"Failed to update address: {str(e)}")


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "user", "address", "city",
                  "province", "is_active", "created_at"]
        read_only_fields = ["user"]


class AddressSimpleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        lookup_field="id", view_name="address-detail")

    class Meta:
        model = Address
        fields = ["address", "is_active", "created_at", "url"]


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = serializers.HyperlinkedRelatedField(
        queryset=Product.objects.all(),
        view_name="product-detail",
        lookup_field="slug"
    )

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'product', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['user', 'rating', 'comment']

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a review.")
        validated_data["user"] = user
        return super().create(validated_data)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image"]


class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "slug", "title", "description",
                  "unit_price", "category", "color", "size", "stock", "reviews", "images"]

    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        paginator = ReviewPagination()
        page = paginator.paginate_queryset(reviews, self.context['request'])
        serializer = ReviewSerializer(page, many=True, context=self.context)
        return paginator.get_paginated_response(serializer.data).data

    def get_images(self, obj):
        images = obj.images.all()
        serializer = ProductImageSerializer(
            images, many=True, context=self.context)
        return serializer.data


class ProductSimpleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='product-detail',
        lookup_field='slug'
    )

    class Meta:
        model = Product
        fields = ['title', 'unit_price', 'url', 'thumbnail']


class CartItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["product", "quantity"]

    def create(self, validated_data):
        print(self.context)
        cart = self.context['cart']
        product = validated_data['product']
        quantity = validated_data['quantity']
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        return cart_item


class CartItemSimpleSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["product"]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["product", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = [
            "items",
            "label",
            "total_price",
            "is_paid",
            "is_shipped",
            "created_at",
            "updated_at"]


class CartSimpleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="carts-detail", lookup_field="id")
    items = CartItemSimpleSerializer(many=True)

    class Meta:
        model = Cart
        fields = [
            "url",
            "items",
            "id",
            "label",
            "total_price",
            "is_shipped",
            "created_at",]


class CartCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = [
            "id",
            "label",
            "total_price",
            "is_paid",
            "is_shipped",
            "created_at",]

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a cart.")
        validated_data["user"] = user
        return super().create(validated_data)


class CartUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        exclude = ["created_at"]
        read_only_fields = ["__all__"]

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to update a cart.")
        return super().update(instance, validated_data)
