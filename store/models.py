from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db import models

from store.validators import PRODUCT_PRICE_VALIDATORS, STOCK_QUANTITY_VALIDATORS

User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_avatar = models.ImageField(
        null=True, blank=True, upload_to='profiles/', verbose_name=_("Profile Avatar"))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.user.phone_number}"

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")


class Address(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                             related_name='addresses', verbose_name=_("User"))

    city = models.CharField(max_length=255, blank=True,
                            null=True, verbose_name=_("City"))

    province = models.CharField(max_length=255, blank=True,
                                null=True, verbose_name=_("Province"))

    address = models.TextField(verbose_name=_("Address"))

    def __str__(self):
        return f"{self.address}"

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")


class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='images', verbose_name=_("Product"))
    image = models.ImageField(upload_to='products/', verbose_name=_("Image"))

    def __str__(self):
        return f"{self.product.title}"

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")


class Product(models.Model):
    title = models.CharField(
        max_length=255, blank=False, verbose_name=_("Title"))

    slug = models.SlugField(verbose_name=_("Slug"), unique=True, blank=True)

    description = models.TextField(verbose_name=_("Description"))

    unit_price = models.DecimalField(
        max_digits=20, decimal_places=2, verbose_name=_("Price"), validators=PRODUCT_PRICE_VALIDATORS)

    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Category"))

    color = models.ManyToManyField(
        "Color", blank=True, verbose_name=_("Color"))

    size = models.ManyToManyField(
        "Size", blank=True, verbose_name=_("Size"))

    stock = models.PositiveIntegerField(verbose_name=_(
        "Stock"), validators=STOCK_QUANTITY_VALIDATORS)

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        self.slug = slugify(f"prd-{self.title}")
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2083)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class SizeValues(models.TextChoices):

    XS = "XS", _("XS")
    S = "S", _("S")
    M = "M", _("M")
    L = "L", _("L")
    XL = "XL", _("XL")
    XXL = "XXL", _("XXL")
    XXXL = "XXXL", _("XXXL")


class Size(models.Model):

    value = models.CharField(max_length=5, verbose_name=_(
        "Value"), choices=SizeValues.choices, default=SizeValues.M)

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = _("Size")
        verbose_name_plural = _("Sizes")


class Color(models.Model):
    value = models.CharField(max_length=255, verbose_name=_("Value"))

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="carts", verbose_name=_("User")
    )
    total_price = models.DecimalField(
        max_digits=20, decimal_places=2, verbose_name=_("Total Price"), default=0
    )

    is_paid = models.BooleanField(default=False, verbose_name=_("Is Paid"))

    is_shipped = models.BooleanField(
        default=False, verbose_name=_("Is Shipped"))

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.user.phone_number} - {self.created_at.strftime('%Y-%m-%d')}"

    def add_item(self, product, quantity=1):
        """
        Add a product to the cart or update its quantity if already exists.
        """
        item, created = CartItem.objects.get_or_create(
            cart=self, product=product)
        if not created:
            item.quantity += quantity
            item.save()
        self.calculate_total_price()

    def calculate_total_price(self):
        """
        Recalculate the total price based on all cart items.
        """
        self.total_price = sum(item.price for item in self.items.all())
        self.save()

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")


class CartItem(models.Model):
    cart = models.ForeignKey(
        "Cart", on_delete=models.CASCADE, related_name="items", verbose_name=_("Cart")
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="cart_items", verbose_name=_("Product")
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantity"), default=1)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At"))

    price = models.DecimalField(
        max_digits=20, decimal_places=2, verbose_name=_("Price"), default=0
    )

    def __str__(self):
        return f"{self.product.title} - {self.cart.user.phone_number}"

    def save(self, *args, **kwargs):
        """
        Automatically update the item price before saving.
        """
        self.price = self.product.unit_price * self.quantity
        super().save(*args, **kwargs)
        self.cart.calculate_total_price()

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")


class OrderStatus(models.TextChoices):
    PENDING = "Pending", _("Pending")
    SHIPPED = "Shipped", _("Shipped")
    DELIVERED = "Delivered", _("Delivered")
    CANCELED = "Canceled", _("Canceled")


class Order(models.Model):

    cart = models.OneToOneField(
        "Cart", on_delete=models.CASCADE, related_name="order", verbose_name=_("Cart")
    )
    shipping_address = models.ForeignKey(
        "Address", on_delete=models.CASCADE, related_name="orders", verbose_name=_("Shipping Address"))

    payment_method = models.CharField(
        max_length=255, verbose_name=_("Payment Method"))

    order_status = models.CharField(
        max_length=255, verbose_name=_("Order Status"),
        choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At"))

    is_shipped = models.BooleanField(
        default=False, verbose_name=_("Is Shipped"))
    is_delivered = models.BooleanField(
        default=False, verbose_name=_("Is Delivered"))

    order_total_price = models.DecimalField(
        max_digits=20, decimal_places=2, verbose_name=_("Order Total Price"), default=0)

    def __str__(self):
        return f"{self.cart.user.phone_number} - {self.created_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        if self.pk:
            total_price = sum(item.price for item in self.items.all())

            if self.order_total_price != total_price:
                self.order_total_price = total_price

        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return sum(item.price for item in self.items.all())

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")


class OrderItem(models.Model):
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="items", verbose_name=_("Order")
    )

    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="order_items", verbose_name=_("Product")
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantity"), default=1)

    price = models.DecimalField(verbose_name=_(
        "Price"), max_digits=20, decimal_places=2)

    def __str__(self):
        return f"{self.product.title} - {self.order.cart.user.phone_number}"

    def save(self, *args, **kwargs):
        self.price = self.product.unit_price * self.quantity
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")


class Payment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payments", verbose_name=_("User"))
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment", verbose_name=_("Order"))
    transaction_id = models.CharField(
        max_length=255, unique=True, verbose_name=_("Transaction ID"))
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    is_successful = models.BooleanField(
        default=False, verbose_name=_("Is successful"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created at"))

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount}"

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


class Review(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews", verbose_name=_("User"))
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews", verbose_name=_("Product"))
    rating = models.PositiveIntegerField(
        default=1, verbose_name=_("Rating"))  # 1 to 5 stars
    comment = models.TextField(
        blank=True, null=True, verbose_name=_("Comment"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"{self.user.username} - {self.rating} stars"

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Code"))
    discount_percentage = models.PositiveIntegerField(
        verbose_name=_("Discount Percentage"))
    valid_from = models.DateTimeField(verbose_name=_("Valid From"))
    valid_to = models.DateTimeField(verbose_name=_("Valid To"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")


class Wishlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist", verbose_name=_("User"))
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlists", verbose_name=_("Product"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")
