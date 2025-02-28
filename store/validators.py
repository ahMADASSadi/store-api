from django.core.validators import MinValueValidator, MaxValueValidator


PRODUCT_PRICE_VALIDATORS = [MinValueValidator(0), MaxValueValidator(1000000)]
STOCK_QUANTITY_VALIDATORS = [MinValueValidator(0), MaxValueValidator(10000)]
