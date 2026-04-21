from django.db import transaction

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.services.event_bus import EventBus

from orders.models import Order
from payments.services.core import mark_order_paid
from payments.services.manager import capture_payment


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_verify_payment(request):
    paypal_id = request.data.get("paypal_id")

    if not paypal_id:
        return Response({"error": "Missing paypal_id"}, status=400)

    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(
                payment_id=paypal_id,
                user=request.user
            )

            if order.status == "PAID":
                return Response({"status": "already_paid", "order_id": order.id})

            success = capture_payment(order, "paypal")

            if not success:
                return Response({"error": "Capture failed"}, status=400)

            mark_order_paid(order, payment_id=paypal_id, provider="paypal")

    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)
    
    EventBus.publish("order_paid", {"order_id": order.id})
    return Response({
        "status": "paid",
        "order_id": order.id
    })