from django.db.models.signals import post_save
from django.dispatch import receiver


from store.models import Order


@receiver(post_save, sender=Order)
def update_order_total_price(sender, instance, **kwargs):
    """Update order total price after saving the order."""
    total_price = sum(item.price for item in instance.items.all())

    if instance.order_total_price != total_price:  # Avoid unnecessary updates
        instance.order_total_price = total_price
        instance.save(update_fields=["order_total_price"])