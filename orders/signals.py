from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Order, OrderItem

@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_status(sender, instance, **kwargs):
    order = instance.order
    # Check if any item is a MAP and has no price
    pending_maps = order.items.filter(item_type='MAP', price__isnull=True).exists()

    if pending_maps:
        if order.status != 'PENDING_PRICE':
            order.status = 'PENDING_PRICE'
            order.save()
    else:
        # All maps have prices, or no maps
        # If status was PENDING_PRICE, move to AWAITING_PAYMENT
        # But only if it was pending price. If it was already PAID, don't revert.
        if order.status == 'PENDING_PRICE':
             order.status = 'AWAITING_PAYMENT'
             order.save()
