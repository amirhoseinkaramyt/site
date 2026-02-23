from django.test import TestCase
from django.contrib.auth.models import User
from .models import Order, OrderItem
from django.core.files.uploadedfile import SimpleUploadedFile

class OrderFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_order_flow(self):
        # 1. Create Order
        order = Order.objects.create(user=self.user)
        self.assertEqual(order.status, 'PENDING_PRICE')

        # 2. Add Circle Item
        circle = OrderItem.objects.create(order=order, item_type='CIRCLE', dimension=100)
        # Check if status updated. Signal should handle it.
        # But wait, create() doesn't trigger post_save on Order? No, but post_save on OrderItem triggers order.save() which might check status.
        # My signal logic checks status on OrderItem save.

        # Reload order from DB
        order.refresh_from_db()
        # Circle has price immediately. So status should be AWAITING_PAYMENT.
        self.assertEqual(order.status, 'AWAITING_PAYMENT')
        self.assertTrue(circle.price > 0)

        # 3. Add Map Item
        # Mock file
        map_file = SimpleUploadedFile("test_map.dxf", b"file_content")
        map_item = OrderItem.objects.create(order=order, item_type='MAP', map_file=map_file)

        order.refresh_from_db()
        # Map has no price yet. Status should be PENDING_PRICE.
        self.assertEqual(order.status, 'PENDING_PRICE')
        self.assertIsNone(map_item.price)

        # 4. Admin sets price
        map_item.price = 50000
        map_item.save()

        order.refresh_from_db()
        # All items have prices. Status should be AWAITING_PAYMENT.
        self.assertEqual(order.status, 'AWAITING_PAYMENT')

        # 5. User uploads receipt
        receipt_file = SimpleUploadedFile("receipt.jpg", b"image_content", content_type="image/jpeg")
        order.receipt = receipt_file
        order.status = 'PAYMENT_UPLOADED' # In view, we set this manually.
        order.save()

        order.refresh_from_db()
        self.assertEqual(order.status, 'PAYMENT_UPLOADED')

        # 6. Admin approves payment
        order.status = 'PAID'
        order.save()

        order.refresh_from_db()
        self.assertEqual(order.status, 'PAID')
