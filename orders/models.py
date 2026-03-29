from django.db import models
from django.conf import settings

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    # BUYER INFO
    buyer_name = models.CharField(max_length=255, null=True, blank=True)
    buyer_email = models.CharField(max_length=255, null=True, blank=True)
    buyer_phone = models.CharField(max_length=20, null=True, blank=True)

    # PAYMENT INFO
    payment_provider = models.CharField(max_length=20, null=True, blank=True)
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def get_total_price(self):
        return sum(
            item.ticket_type.price * item.quantity
            for item in self.items.all()
        )

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    ticket_type = models.ForeignKey("events.TicketType", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    qr_code = models.ImageField(upload_to="qrcodes/", null=True, blank=True)

class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    ticket_type = models.ForeignKey("events.TicketType", on_delete=models.CASCADE)

    qr_code = models.ImageField(upload_to="qrcodes/")
    is_used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)