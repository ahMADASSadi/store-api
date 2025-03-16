# your_app/filters.py
import django_filters
from store.models import Product


class ProductFilter(django_filters.FilterSet):
    promotion = django_filters.BooleanFilter(field_name='promotions__is_valid')
    category = django_filters.CharFilter(
        field_name='category__name', lookup_expr='exact')
    color = django_filters.CharFilter(
        field_name='color__value', lookup_expr='icontains')
    size = django_filters.CharFilter(
        field_name='size__value', lookup_expr='icontains')
    min_price = django_filters.NumberFilter(
        field_name='unit_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(
        field_name='unit_price', lookup_expr='lte')
    title = django_filters.CharFilter(
        field_name='title', lookup_expr='icontains')
    brand = django_filters.CharFilter(
        field_name="brand__slug", lookup_expr="icontains")
    is_available = django_filters.BooleanFilter(field_name='is_available')

    class Meta:
        model = Product
        fields = ['category', 'color', 'size', 'min_price',
                  'max_price', 'title', "is_available"]
