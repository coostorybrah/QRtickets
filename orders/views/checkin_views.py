from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Ticket


@api_view(["POST"])
@permission_classes([IsAuthenticated])  # later: staff-only
def api_check_in_ticket(request):
    ticket_id = request.data.get("ticket_id")

    if not ticket_id:
        return Response({"error": "Missing ticket_id"}, status=400)

    try:
        ticket = Ticket.objects.select_related(
            "ticket_type__event"
        ).get(id=ticket_id)
    except Ticket.DoesNotExist:
        return Response({"error": "Invalid ticket"}, status=404)

    if ticket.is_used:
        return Response({"error": "Ticket already used"}, status=400)

    ticket.is_used = True
    ticket.save()

    return Response({
        "status": "success",
        "event": ticket.ticket_type.event.name,
        "ticket_type": ticket.ticket_type.name
    })