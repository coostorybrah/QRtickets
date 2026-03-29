from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from orders.services.order_service import create_order, add_items, pay_order, cancel_order

# CHECK ORDER STATUS
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    return Response({
        "status": order.status
    })

# PAYMENT
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_pay_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    provider = request.GET.get("provider", "paypal")

    payment_url, error = pay_order(order, provider)

    if error:
        return Response({"error": error}, status=400)

    return Response({"payment_url": payment_url})

# API CREATE ORDER
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_create_order(request):
    order, error = create_order(
        request.user,
        request.data.get("buyer_name"),
        request.data.get("buyer_email"),
        request.data.get("buyer_phone")
    )

    if error:
        return Response({"error": error}, status=400)

    return Response({
        "status": "success",
        "order_id": order.id
    })


# API CANCEL ORDER
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    error = cancel_order(order)

    if error:
        return Response({"error": error}, status=400)

    return Response({"status": "cancelled"})

# API USER TICKETS (FOR "MY TICKET" PAGE)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_my_tickets(request):

    orders = (
        Order.objects
        .filter(user=request.user, status__in=["PAID", "COMPLETED"])
        .prefetch_related("tickets__ticket_type__event")
    )

    data = []

    for order in orders:
        for ticket in order.tickets.all():
            data.append({
                "ticket_id": ticket.id,
                "event": ticket.ticket_type.event.name,
                "ticket_type": ticket.ticket_type.name,
                "qr_code": ticket.qr_code.url,
                "is_used": ticket.is_used,
                "date": ticket.ticket_type.event.date,
                "time": ticket.ticket_type.event.start_time,
            })

    return Response(data)


# API ADD ITEMS
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_add_items(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    error = add_items(order, request.data.get("items", []))

    if error:
        return Response({"error": error}, status=400)

    return Response({"status": "success"})

