from django.contrib import admin

from store.models import Product, Category, ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category']
    search_fields = ['name', 'category']
    list_filter = ['category']
    list_editable = ['price', 'stock']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']
    search_fields = ['product']
    list_filter = ['product']
