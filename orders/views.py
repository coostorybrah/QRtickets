import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from orders.models import Order

# Create your views here.
@login_required(login_url='login')
def payments(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required.'}, status=405)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'}, status=400)

    order_number = body.get('orderID', '')

    try:
        order = Order.objects.get(
            user=request.user,
            is_ordered=False,
            order_number=order_number,
        )
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found.'}, status=404)

    order.is_ordered = True
    order.status = 'Completed'
    order.save()

    # Send order received email to customer
    try:
        mail_subject = 'Xác nhận đặt vé thành công - QRtickets'
        message = render_to_string('orders/order_recieved_email.html', {
            'user': request.user,
            'order': order,
            'order_items': order.items.select_related('product').all(),
        })
        send_email = EmailMessage(mail_subject, message, to=[request.user.email])
        send_email.send(fail_silently=True)
    except Exception:
        pass

    return JsonResponse({'status': 'ok', 'order_number': order.order_number})
