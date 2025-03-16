from django.utils import timezone
from django.db.transaction import atomic
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


from store.models import Order, UserProfile, Product, ProductImage


User = get_user_model()


@receiver(post_save, sender=Order)
def update_order_total_price(sender, instance, **kwargs):
    """Update order total price after saving the order."""
    total_price = sum(item.price for item in instance.items.all())

    if instance.order_total_price != total_price:
        instance.order_total_price = total_price
        instance.save(update_fields=["order_total_price"])


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=ProductImage)
def update_product_thumbnail(sender, instance, created, **kwargs):
    """Update the Product's thumbnail when a new ProductImage is created."""
    if created:
        product = instance.product
        if not product.thumbnail:
            product.thumbnail = instance.image
            product.save(update_fields=['thumbnail'])
