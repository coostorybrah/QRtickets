from django.core.cache import cache

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Ticket, CheckInLog

# API CHECK-IN
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_check_in_ticket(request):
        
    key = f"scan_rate_{request.user.id}"
    count = cache.get(key, 0)

    if count >= 10:
        return Response({"error": "Too many requests"}, status=429)

    cache.set(key, count + 1, timeout=10)
    
    ticket_id = request.data.get("ticket_id")

    if not ticket_id:
        return Response({"error": "Missing ticket_id"}, status=400)

    try:
        ticket = Ticket.objects.select_related(
            "ticket_type__event__organizer"
        ).get(id=ticket_id)
    except Ticket.DoesNotExist:
        return Response({"error": "Invalid ticket"}, status=404)

    event = ticket.ticket_type.event

    # 🔥 Ownership check
    if not hasattr(request.user, "organizer"):
        return Response({"error": "Not an organizer"}, status=403)

    if event.organizer_id != request.user.organizer.id:
        return Response({"error": "Not allowed for this event"}, status=403)

    # ❌ Already used
    if ticket.is_used:
        return Response({"error": "Ticket already used"}, status=400)

    already_used = ticket.is_used

    CheckInLog.objects.create(
        ticket = ticket,
        scanned_by = request.user.organizer.id,
        success = not already_used
    )

    if already_used:
        return Response({"error": "Ticket already used"}, status=400)

    # ✅ Mark used
    ticket.is_used = True
    ticket.save()
    
    return Response({
        "status": "success",
        "event": event.name,
        "ticket_type": ticket.ticket_type.name
    })