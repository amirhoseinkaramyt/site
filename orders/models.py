from django.db import models
from django.contrib.auth.models import User
import math

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING_PRICE', 'Pending Price'), # Waiting for admin to set price for maps
        ('AWAITING_PAYMENT', 'Awaiting Payment'), # Price is set, waiting for user to upload receipt
        ('PAYMENT_UPLOADED', 'Payment Uploaded'), # User uploaded receipt, waiting for admin approval
        ('PAID', 'Paid'), # Admin approved payment
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_PRICE')
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_total_price(self):
        # Calculate total price based on items
        total = 0
        all_priced = True
        for item in self.items.all():
            if item.price is not None:
                total += item.price
            else:
                all_priced = False
        return total, all_priced

    @property
    def current_total_price(self):
        total, _ = self.update_total_price()
        return total

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} ({self.get_status_display()})"


class OrderItem(models.Model):
    ITEM_TYPES = [
        ('CIRCLE', 'Circle'),
        ('SQUARE', 'Square'),
        ('MAP', 'Map (DXF/DWG)'),
    ]
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    # Dimensions in mm
    dimension = models.FloatField(help_text="Dimension in mm (Radius for Circle, Side for Square)", null=True, blank=True)
    map_file = models.FileField(upload_to='maps/', null=True, blank=True)

    weight = models.FloatField(null=True, blank=True, help_text="Weight in kg")
    price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, help_text="Price in Tomans")

    def calculate_price_and_weight(self):
        if self.item_type == 'CIRCLE':
            if self.dimension:
                # Area = pi * r^2
                area = math.pi * (self.dimension ** 2)
                # Weight = Area * 0.00000785
                self.weight = area * 0.00000785
                # Price = Weight * 70000
                self.price = round(self.weight * 70000)
        elif self.item_type == 'SQUARE':
            if self.dimension:
                # Area = side^2
                area = self.dimension ** 2
                self.weight = area * 0.00000785
                self.price = round(self.weight * 70000)
        elif self.item_type == 'MAP':
            # Price set by admin manually
            pass

    def save(self, *args, **kwargs):
        # Recalculate only if not set or if dimensions changed?
        # For simplicity, always recalculate for non-MAP items unless price is manually set (which shouldn't happen for auto items)
        # But wait, if admin edits price of circle? Maybe we should allow it.
        # But for now, enforce calculation for Circle/Square.
        if self.item_type != 'MAP':
             self.calculate_price_and_weight()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_item_type_display()} - Order #{self.order.id}"
