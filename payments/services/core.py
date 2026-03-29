from django.db import transaction
from django.utils import timezone

from orders.models import Order
from orders.services.event_bus import EventBus


def mark_order_paid(order: Order, payment_id=None, provider=None):
    if order.status == "PAID":
        return

    with transaction.atomic():
        order.status = "PAID"
        order.payment_id = payment_id
        order.payment_provider = provider
        order.paid_at = timezone.now()
        order.save()
        
        for item in order.items.select_related("ticket_type"):
            ticket_type = item.ticket_type
            ticket_type.quantity_sold += item.quantity
            ticket_type.save()

    EventBus.publish("order_paid", {"order_id": order.id})


def mark_order_failed(order: Order):
    if order.status in ["PAID", "CANCELLED"]:
        return

    order.status = "FAILED"
    order.save()


def validate_order_amount(order: Order, amount):
    return float(order.get_total_price()) == float(amount)