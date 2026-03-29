from orders.models import OrderItem, Ticket
import qrcode
from io import BytesIO
from django.core.files import File

def generate_qr_for_order(order_id):
    items = OrderItem.objects.filter(order_id=order_id)

    # prevent duplicate generation
    if Ticket.objects.filter(order_id=order_id).exists():
        return

    for item in items:
        for _ in range(item.quantity):

            ticket = Ticket.objects.create(
                order=item.order,
                order_item=item,
                ticket_type=item.ticket_type
            )

            data = f"ticket:{ticket.id}"

            qr = qrcode.make(data)

            buffer = BytesIO()
            qr.save(buffer, format="PNG")

            filename = f"qr_{ticket.id}.png"
            ticket.qr_code.save(filename, File(buffer), save=True)