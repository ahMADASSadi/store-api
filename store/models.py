from django.db import models

# Create your models here.


class ProductImage(models.Model):
    image = models.ImageField(upload_to='products/')
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return self.product.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    description = models.CharField(max_length=2083)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2083)

    def __str__(self):
        return self.name
