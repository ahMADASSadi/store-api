from uuid import uuid4

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.db import models

from store.validators import PRODUCT_PRICE_VALIDATORS, STOCK_QUANTITY_VALIDATORS
from store.utility import Utility

User = get_user_model()
utility = Utility()


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_avatar = models.ImageField(
        null=True, blank=True, upload_to='profiles/', verbose_name=_("Profile Avatar"))
    email = models.EmailField(unique=True, null=True,
                              blank=True, verbose_name=_("Email"))
    first_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("First Name"))
    last_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Last Name"))
    username = models.CharField(
        max_length=250, null=True, blank=True, unique=True, verbose_name=_("Username"))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.user.phone_number}"

    class Meta:
        ordering = ["username"]
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        indexes = [models.Index(fields=['user'])]


class Address(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                             related_name='addresses', verbose_name=_("User"))
    city = models.CharField(max_length=255, blank=True,
                            null=True, verbose_name=_("City"))
    province = models.CharField(max_length=255, blank=True,
                                null=True, verbose_name=_("Province"))
    address = models.TextField(verbose_name=_("Address"))
    is_active = models.BooleanField(default=False, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"{self.address}"

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        constraints = [
            models.UniqueConstraint(
                name="active_address",
                fields=["user"],
                condition=models.Q(is_active=True)
            )
        ]
        indexes = [models.Index(fields=['user'])]


class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='images', verbose_name=_("Product"))
    image = models.ImageField(upload_to='products/', verbose_name=_("Image"))
    alt_text = models.CharField(max_length=255, verbose_name=_("Alt Text"))

    def __str__(self):
        return f"{self.product.title}"

    def save(self, *args, **kwargs):
        if not self.alt_text:
            self.alt_text = self.product.title
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        indexes = [models.Index(fields=['product'])]


class RevewImage(models.Model):
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='review_images', verbose_name=_("Product"))
    review = models.ForeignKey("Review", on_delete=models.SET_NULL, verbose_name=_(
        "Review"), related_name="images", null=True, blank=True)
    image = models.ImageField(upload_to='products/', verbose_name=_("Image"))
    alt_text = models.CharField(max_length=255, verbose_name=_("Alt Text"))

    def __str__(self):
        return f"{self.product.title}"

    def save(self, *args, **kwargs):
        if not self.alt_text:
            self.alt_text = f"{self.review.comment:20}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        indexes = [models.Index(fields=['product']),
                   models.Index(fields=['review'])]


class Discount(models.Model):
    product = models.ManyToManyField("Product",
                                     related_name="discount", verbose_name=_("Product"))
    discount_percentage = models.DecimalField(
        max_digits=2, decimal_places=0, verbose_name=_("Discount Percentage"))
    description = models.CharField(
        verbose_name=_("Description"), max_length=255)
    start_date = models.DateTimeField(verbose_name=_("Start Date"))
    end_date = models.DateTimeField(verbose_name=_("End Date"))

    def __str__(self):
        return f"{self.description:20} - {self.discount_percentage}%"

    def check_validity(self):
        """Check if the promotion is currently valid based on start and end dates."""
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        [product.calculate_discount() for product in self.product.all()]

    class Meta:
        ordering = ["-end_date"]
        verbose_name = _("Promotion")
        verbose_name_plural = _("Promotions")


class Brand(models.Model):
    title = models.CharField(_("Title"), max_length=255, unique=True)
    slug = models.SlugField(_("Slug"), unique=True, blank=True, db_index=True)
    logo = models.ImageField(
        _("Logo"), upload_to="logos/", null=True, blank=True)
    description = models.TextField(_("Description"), blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        self.slug = utility.persian_slugify("brd", self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")


class Product(models.Model):
    title = models.CharField(
        max_length=255, blank=False, verbose_name=_("Title"))
    slug = models.SlugField(verbose_name=_(
        "Slug"), unique=True, blank=True, db_index=True)
    brand = models.ManyToManyField(
        "Brand", blank=True, verbose_name=_("Brands"))
    description = models.TextField(verbose_name=_("Description"))
    unit_price = models.DecimalField(
        max_digits=20, decimal_places=2, verbose_name=_("Price"), validators=PRODUCT_PRICE_VALIDATORS)
    discount_price = models.DecimalField(
        max_digits=20, decimal_places=2, verbose_name=_("Discount Price"), blank=True, null=True)
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("Category"))
    color = models.ManyToManyField(
        "Color", blank=True, verbose_name=_("Color"))
    size = models.ManyToManyField(
        "Size", blank=True, verbose_name=_("Size"))
    stock = models.PositiveIntegerField(verbose_name=_(
        "Stock"), validators=STOCK_QUANTITY_VALIDATORS)
    is_available = models.BooleanField(_("Is Available"), default=True)
    thumbnail = models.ImageField(verbose_name=_(
        "Thumbnail"), upload_to="thumbnails/", null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.title}"

    def has_enough_stock(self, quantity):
        return self.stock >= quantity

    def reduce_stock(self, quantity):
        if self.has_enough_stock(quantity):
            self.stock -= quantity
            self.save()
            return True
        return False

    def calculate_discount(self):
        """
        Calculate the discount price based on the most recent valid promotion.
        Updates discount_price if a valid promotion exists, otherwise sets it to None.
        """
        valid_promotion = self.promotions.filter(
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
            # Get the most recent valid promotion
        ).order_by('-start_date').first()

        if valid_promotion:
            discount_percentage = valid_promotion.discount_percentage
            self.discount_price = self.unit_price * (1 - discount_percentage)
        else:
            self.discount_price = None
        self.save(update_fields=['discount_price'])

    @property
    def current_price(self):
        """Return the discount price if available, otherwise the unit price."""
        return self.discount_price if self.discount_price is not None else self.unit_price

    def check_avaliablity(self):
        return self.stock > 0

    def save(self, *args, **kwargs):
        self.is_available = self.check_avaliablity()
        self.slug = utility.persian_slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    slug = models.SlugField(verbose_name=_("Slug"), max_length=300)
    description = models.CharField(
        max_length=2083, verbose_name=_("Description"))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = utility.persian_slugify("cat", self.name)
        super().save(*args, **kwargs)

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


class ColorValue(models.TextChoices):
    RED = "RED", _("Red")
    BLUE = "BLUE", _("Blue")
    GREEN = "GREEN", _("Green")
    YELLOW = "YELLOW", _("Yellow")
    WHITE = "WHITE", _("White")
    BLACK = "BLACK", _("Black")
    GRAY = "GRAY", _("Gray")


class Color(models.Model):
    value = models.CharField(max_length=255, verbose_name=_(
        "Value"), choices=ColorValue.choices, default=ColorValue.WHITE)

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = _("Color")
        verbose_name_plural = _("Colors")


class Cart(models.Model):
    CART_LABELS = (
        ('Primary', _('Primary')),
        ('Secondary', _('Secondary')),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="carts", verbose_name=_("User")
    )

    label = models.CharField(
        max_length=20,
        choices=CART_LABELS,
        verbose_name=_("Cart Label"),
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.user.phone_number} - {self.created_at.strftime('%Y-%m-%d')}"

    def calculate_total_price(self):
        """
        Recalculate the total price based on all cart items.
        """
        return sum(item.unit_price * item.quantity for item in self.items.all())

    def save(self, *args, **kwargs):
        """Override save to assign label based on creation order."""
        if not self.pk:
            existing_carts = Cart.objects.filter(
                user=self.user).order_by('created_at')
            current_count = existing_carts.count()

            if current_count >= 2:
                raise ValidationError(
                    _("User already has the maximum of 2 carts."),
                    code="max_carts_exceeded"
                )

            if current_count == 0:
                self.label = 'Primary'
            elif current_count == 1:
                self.label = 'Secondary'

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['created_at']
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


class Order(models.Model):
    PENDING_STATUS = 'p'
    SHIPPED_STATUS = 's'
    DELIVERED_STATUS = 'd'
    CANCELED_STATUS = 'c'

    ORDER_STATUS_CHOICES = [
        (PENDING_STATUS, _("Pending")),
        (SHIPPED_STATUS, _("Shipped")),
        (DELIVERED_STATUS, _("Delivered")),
        (CANCELED_STATUS, _("Canceled")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", verbose_name=_("User"))

    cart = models.OneToOneField(
        "Cart", on_delete=models.SET_NULL, related_name="order", verbose_name=_("Cart"), null=True, blank=True
    )
    shipping_address = models.ForeignKey(
        "Address", on_delete=models.CASCADE, related_name="orders", verbose_name=_("Shipping Address"))

    order_status = models.CharField(
        max_length=255, verbose_name=_("Order Status"),
        choices=ORDER_STATUS_CHOICES, default=PENDING_STATUS
    )

    is_shipped = models.BooleanField(
        default=False, verbose_name=_("Is Shipped"))

    is_delivered = models.BooleanField(
        default=False, verbose_name=_("Is Delivered"))

    order_total_price = models.DecimalField(
        max_digits=20, decimal_places=2, verbose_name=_("Order Total Price"), default=0)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"{self.cart.user.phone_number} - {self.created_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        print(self.cart.items)
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
    PENDING_STATUS = 'p'
    SUCCESS_STATUS = 's'
    FAILED_STATUS = 'f'
    REFUNDED_STATUS = 'r'

    PAYMENT_STATUS_CHOICES = [
        (PENDING_STATUS, _("Pending")),
        (SUCCESS_STATUS, _("Success")),
        (FAILED_STATUS, _("Failed")),
        (REFUNDED_STATUS, _("Refunded")),
    ]

    transaction_id = models.UUIDField(
        default=uuid4, unique=True, verbose_name=_("Transaction ID"), primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payments", verbose_name=_("User"))
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment", verbose_name=_("Order"))
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Amount"))

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PENDING_STATUS
    )
    payment_date = models.DateTimeField(
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
        default=1, verbose_name=_("Rating"))
    comment = models.TextField(
        blank=True, null=True, verbose_name=_("Comment"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"{self.user.phone_number} - {self.rating} stars"

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")


class Wishlist(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist", verbose_name=_("User"))
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlists", verbose_name=_("Product"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")
