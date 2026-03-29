from django.core.mail import send_mail
from orders.models import Order


def send_order_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return

    tickets = order.tickets.select_related("ticket_type__event")

    message = f"Hello {order.buyer_name},\n\nYour tickets:\n\n"

    for t in tickets:
        message += (
            f"- {t.ticket_type.event.name} | "
            f"{t.ticket_type.name} | "
            f"QR: {t.qr_code.url}\n"
        )

    send_mail(
        subject="Your Ticket is Ready 🎫",
        message=message,
        from_email="noreply@qrticket.com",
        recipient_list=[order.buyer_email],
        fail_silently=False,
    )