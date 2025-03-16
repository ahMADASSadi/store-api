from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend

from store.serializers import (AddressSerializer, AddressCreateSerializer, AddressSimpleSerializer, AddressUpdateSerializer,
                               CartCreateSerializer, CartItemCreateSerializer, CartItemSerializer, CartItemSimpleSerializer, CartSerializer, CartSimpleSerializer, CartUpdateSerializer,
                               ProductSerializer, ProductSimpleSerializer, ReviewCreateSerializer, ReviewSerializer, UserProfileSerializer, UserProfileUpdateSerializer)
from store.models import Product, Review, UserProfile, Address, Cart, CartItem
from store.paginations import ProductHomePagination
from store.permissions import IsOwnProfile
from store.filters import ProductFilter


User = get_user_model()


class UserProfileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnProfile]

    def get_queryset(self):
        user = self.request.user
        return UserProfile.objects.select_related("user").filter(user=user)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddressViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        queryset = Address.objects.select_related('user').prefetch_related(
            'user__user'
        ).filter(user__user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return AddressUpdateSerializer
        elif self.action == "create":
            return AddressCreateSerializer
        elif self.action == "retrieve":
            return AddressSerializer
        return AddressSimpleSerializer


class ProductViewSet(ModelViewSet):
    http_method_names = ["get"]
    
    pagination_class = ProductHomePagination
    
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['unit_price', 'title', 'created_at']
    
    queryset = Product.objects.select_related(
        "category").prefetch_related("color", "size").all()
    
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductSerializer
        return ProductSimpleSerializer

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        slug = self.kwargs.get(self.lookup_field)
        obj = get_object_or_404(queryset, slug=slug)
        self.check_object_permissions(self.request, obj)
        return obj


class ReviewViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Review.objects.select_related("product", "user").filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer


class CartViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnProfile]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.select_related("user").prefetch_related("items").all()

    def get_serializer_class(self):
        print(self.action)
        if self.action == "create":
            return CartCreateSerializer
        elif self.action in ("update", "partial_update"):
            return CartUpdateSerializer
        elif self.action == "retrieve":
            return CartSerializer
        return CartSimpleSerializer


class CartItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnProfile]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        cart = Cart.objects.prefetch_related(
            "items").select_related("user").filter(user=user).first()
        return CartItem.objects.prefetch_related("user").select_related("cart", "product").filter(cart=cart).all()

    def get_serializer_class(self):
        if self.action == "create":
            return CartItemCreateSerializer
        elif self.action in ("update", "partial_update"):
            return CartItemUpdateSerializer
        elif self.action == "retrieve":
            return CartItemSerializer
        return CartItemSimpleSerializer
