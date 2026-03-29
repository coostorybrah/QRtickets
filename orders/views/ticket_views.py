from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order


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