from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.contrib import admin


from store.models import (Brand, Product, Category, ProductImage, Discount, Size,
                          Color, Cart, CartItem, OrderItem, UserProfile, Order, Address, Review)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    min_num = 1
    max_num = 20
    extra = 0


class ReviewInline(admin.TabularInline):
    model = Review
    min_num = 0
    extra = 0  # Prevent extra empty fields for new entries
    can_delete = False  # Disable delete button
    # Make all fields read-only
    readonly_fields = [field.name for field in Review._meta.fields]

    def has_add_permission(self, request, obj=None):
        return False  # Prevent adding new reviews

    def has_change_permission(self, request, obj=None):
        return False  # Prevent modifying existing reviews

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deleting reviews


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "get_colors",
                    "get_sizes", "unit_price", "stock")
    list_filter = ("category", "color", "size", "stock")
    search_fields = ("title", "description", "category__name")
    inlines = [ProductImageInline, ReviewInline]
    filter_horizontal = ["color", "size"]
    ordering = ("title",)
    list_editable = ("stock", "unit_price")
    readonly_fields = ("slug",)
    actions = ["empty_stock"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("category", "color", "size")

    def get_sizes(self, obj):
        """Display all sizes as a comma-separated list."""
        return ", ".join([size.value for size in obj.size.all()])
    get_sizes.short_description = "Sizes"

    def get_colors(self, obj):
        """Display all colors as a comma-separated list."""
        return ", ".join([color.value for color in obj.color.all()])
    get_colors.short_description = "Colors"

    def save_model(self, request, obj, form, change):
        """Auto-generate slug if empty before saving."""
        obj.slug = slugify(f"prd-{obj.title}")
        super().save_model(request, obj, form, change)

    def empty_stock(self, request, queryset):
        """Clear stock for selected products."""
        queryset.update(stock=0)
        self.message_user(request, _("Stock for selected products cleared."))
    empty_stock.short_description = _("Clear Stock")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image")
    search_fields = ("product__title",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "rating", "created_at"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name", "description")


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("description",
                    "discount_percentage", "start_date", "end_date")
    list_filter = ("start_date", "end_date")
    list_display_links = ("description",)
    list_editable = ("discount_percentage",)
    actions = ["devalidate_Discount"]

    def devalidate_Discount(self, request, queryset):
        queryset.update(end_date=timezone.now())
        self.message_user(request, _("Discounts deactivated successfully."))
    devalidate_Discount.short_description = _("Deactivate Discounts")


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("value",)
    list_filter = ("value",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("value",)


# class CartItemInline(admin.TabularInline):
#     model = CartItem
#     extra = 0
#     readonly_fields = ("price",)
#     fields = ("product", "quantity", "price")


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ("user", "total_price", "is_paid", "created_at", "updated_at")
#     list_filter = ("is_paid", "created_at")
#     search_fields = ("user__phone_number", "user__username")
#     ordering = ("-created_at",)
#     readonly_fields = ("total_price", "created_at", "updated_at")
#     inlines = [CartItemInline]

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.prefetch_related("user", "items__product")


# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ("product", "cart", "quantity",
#                     "price", "created_at", "updated_at")
#     list_filter = ("created_at", "updated_at")
#     search_fields = ("product__title",
#                      "cart__user__phone_number", "cart__user__username")
#     ordering = ("-created_at",)
#     readonly_fields = ("price", "created_at", "updated_at")


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 0
#     readonly_fields = ("price",)
#     fields = ("product", "quantity", "price")


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ("cart", "shipping_address", "order_status", "created_at", "updated_at", "order_total_price")
#     list_filter = ("order_status", "created_at", "updated_at")
#     search_fields = ("cart__user__phone_number",
#                      "cart__user__username", "shipping_address__address")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at", "updated_at", "order_total_price")
#     inlines = [OrderItemInline]

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         return qs.prefetch_related("cart__user", "shipping_address", "items__product")


# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ("product", "order", "quantity", "price")
#     search_fields = ("product__title", "order__cart__user__phone_number",
#                      "order__cart__user__username")
#     readonly_fields = ("price",)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "province", "address")
    search_fields = ("user__user__phone_number", "city", "province", "address")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "profile_avatar", "updated_at")
    search_fields = ("user__phone_number",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["title",
                    "logo",
                    "description",
                    "created_at",]
