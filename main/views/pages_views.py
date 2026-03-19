from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from decimal import Decimal, InvalidOperation
from django.db.models import Prefetch
from datetime import timedelta
from events.models import Event, Venue, Category
from orders.models import Order, OrderItem
from main.services.account_activation import send_account_activation_email
from main.services.user_identity import (
    build_unique_username_from_email,
    get_user_by_email,
    normalize_email,
)

import json

User = get_user_model()
DEFAULT_AVATAR = "/static/images/avatars/default-avatar.png"
ORDER_QR_TIMEOUT = timedelta(minutes=1)


def _expire_stale_orders(user):
    cutoff = timezone.now() - ORDER_QR_TIMEOUT
    Order.objects.filter(user=user, status="pending", created_at__lte=cutoff).update(status="cancelled")


def _build_qr_context(order):
    expires_at = order.created_at + ORDER_QR_TIMEOUT
    return {
        "qr_order": order,
        "qr_expires_at": expires_at,
        "qr_data": (
            f"ORDER:{order.id}|EVENT:{order.event.slug}|TOTAL:{order.total_price}|"
            f"METHOD:{order.payment_method}|EXP:{expires_at.isoformat()}"
        ),
    }

# HOMEPAGE
def home(request):
    return render(request, "trangchu.html")

# PAGE CHI TIET SU KIEN
def event_detail(request, event_id):
    return render(request, "chitietsukien.html", {"event_id": event_id})


def checkout(request):
    if not request.user.is_authenticated:
        return redirect("my_tickets")

    _expire_stale_orders(request.user)

    event_id = request.GET.get("event_id") or request.POST.get("event_id")
    quantity_raw = request.GET.get("quantity") or request.POST.get("quantity") or "1"
    price_raw = request.GET.get("price") or request.POST.get("price")

    event = get_object_or_404(Event, slug=event_id)

    try:
        quantity = max(1, min(3, int(quantity_raw)))
    except (ValueError, TypeError):
        quantity = 1

    try:
        selected_price = Decimal(price_raw)
    except (InvalidOperation, TypeError):
        selected_price = event.min_price or Decimal("0")

    ticket_type = event.ticket_types.filter(price=selected_price).first()
    if ticket_type is None:
        ticket_type = event.ticket_types.order_by("price").first()

    unit_price = ticket_type.price if ticket_type else Decimal("0")
    total_price = unit_price * quantity

    context = {
        "event": event,
        "ticket_type": ticket_type,
        "quantity": quantity,
        "unit_price": unit_price,
        "total_price": total_price,
        "payment_methods": Order.PAYMENT_METHOD_CHOICES,
        "form_error": None,
        "form_values": {
            "customer_name": request.user.get_full_name() or request.user.username,
            "phone_number": "",
            "contact_email": request.user.email or "",
            "payment_method": "bank_transfer",
        },
        "qr_order": None,
        "qr_expires_at": None,
        "qr_data": None,
    }

    if request.method == "POST":
        action = request.POST.get("action", "create")

        if action == "regenerate":
            source_order_id = request.POST.get("source_order_id", "").strip()
            source_order = get_object_or_404(
                Order.objects.select_related("event").prefetch_related("items__ticket_type"),
                id=source_order_id,
                user=request.user,
            )

            source_item = source_order.items.select_related("ticket_type").first()
            if source_item is None or source_order.event is None:
                context["form_error"] = "Không thể tạo lại mã QR vì đơn hàng không hợp lệ."
                return render(request, "checkout.html", context)

            if source_order.status == "pending":
                source_order.status = "cancelled"
                source_order.save(update_fields=["status"])

            regenerated_order = Order.objects.create(
                user=request.user,
                event=source_order.event,
                total_price=source_order.total_price,
                customer_name=source_order.customer_name,
                phone_number=source_order.phone_number,
                contact_email=source_order.contact_email,
                payment_method=source_order.payment_method,
                status="pending",
            )

            OrderItem.objects.create(
                order=regenerated_order,
                ticket_type=source_item.ticket_type,
                quantity=source_item.quantity,
                price=source_item.price,
            )

            context["event"] = source_order.event
            context["ticket_type"] = source_item.ticket_type
            context["quantity"] = source_item.quantity
            context["unit_price"] = source_item.price
            context["total_price"] = regenerated_order.total_price
            context["form_values"] = {
                "customer_name": regenerated_order.customer_name,
                "phone_number": regenerated_order.phone_number,
                "contact_email": regenerated_order.contact_email,
                "payment_method": regenerated_order.payment_method,
            }
            context.update(_build_qr_context(regenerated_order))

            return render(request, "checkout.html", context)

        customer_name = request.POST.get("customer_name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        contact_email = request.POST.get("contact_email", "").strip()
        payment_method = request.POST.get("payment_method", "").strip()

        context["form_values"] = {
            "customer_name": customer_name,
            "phone_number": phone_number,
            "contact_email": contact_email,
            "payment_method": payment_method,
        }

        valid_payment_methods = {method for method, _ in Order.PAYMENT_METHOD_CHOICES}

        if not customer_name or not phone_number or not contact_email:
            context["form_error"] = "Vui lòng điền đầy đủ thông tin thanh toán."
        elif payment_method not in valid_payment_methods:
            context["form_error"] = "Phương thức thanh toán không hợp lệ."
        elif ticket_type is None:
            context["form_error"] = "Không tìm thấy hạng vé hợp lệ."
        else:
            order = Order.objects.create(
                user=request.user,
                event=event,
                total_price=total_price,
                customer_name=customer_name,
                phone_number=phone_number,
                contact_email=contact_email,
                payment_method=payment_method,
                status="pending",
            )

            OrderItem.objects.create(
                order=order,
                ticket_type=ticket_type,
                quantity=quantity,
                price=unit_price,
            )
            context.update(_build_qr_context(order))

    return render(request, "checkout.html", context)


@login_required
def expire_order(request, order_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Phương thức không hợp lệ."}, status=405)

    _expire_stale_orders(request.user)

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == "paid":
        return JsonResponse({"success": False, "message": "Đơn hàng đã thanh toán."}, status=400)

    if order.status == "cancelled":
        return JsonResponse({"success": True, "status": order.status})

    order.status = "cancelled"
    order.save(update_fields=["status"])

    return JsonResponse({"success": True, "status": order.status})

# MY TICKETS PAGE 
def my_tickets(request):
    if request.user.is_authenticated:
        _expire_stale_orders(request.user)

    activated_state = request.GET.get("activated", "").strip()

    next_url = request.GET.get("next", "").strip()
    if next_url and not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ""

    context = {
        "auth_mode": "login",
        "auth_error": None,
        "auth_success": None,
        "next_url": next_url,
        "form_values": {
            "email": "",
        }
    }

    if activated_state == "1":
        context["auth_success"] = "Tài khoản đã được kích hoạt. Bạn có thể đăng nhập ngay bây giờ."
    elif activated_state == "0":
        context["auth_error"] = "Liên kết kích hoạt không hợp lệ hoặc đã hết hạn."

    if request.user.is_authenticated:
        base_orders = (
            Order.objects.filter(user=request.user)
            .select_related("event", "event__venue")
            .prefetch_related(
                Prefetch(
                    "items",
                    queryset=OrderItem.objects.select_related("ticket_type").order_by("created_at"),
                )
            )
            .order_by("-created_at")
        )
        context["paid_orders"] = base_orders.filter(status="paid")
        context["cancelled_orders"] = base_orders.filter(status="cancelled")
        return render(request, "vecuatoi.html", context)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "login":
            email = normalize_email(request.POST.get("email"))
            password = request.POST.get("password", "")
            next_url = request.POST.get("next", next_url).strip()

            context["auth_mode"] = "login"
            context["next_url"] = next_url
            context["form_values"]["email"] = email

            existing_user = get_user_by_email(email)
            user = authenticate(
                request,
                username=existing_user.username if existing_user else "",
                password=password,
            )

            if user is not None:
                login(request, user)
                if next_url:
                    return redirect(next_url)
                return redirect("my_tickets")

            if existing_user and not existing_user.is_active:
                context["auth_error"] = "Tài khoản chưa kích hoạt. Vui lòng mở email để xác nhận đăng ký."
                return render(request, "vecuatoi.html", context)

            context["auth_error"] = "Sai email hoặc mật khẩu."

        elif action == "register":
            email = normalize_email(request.POST.get("email"))
            password = request.POST.get("password", "")
            password_confirm = request.POST.get("password_confirm", "")
            next_url = request.POST.get("next", next_url).strip()

            context["auth_mode"] = "register"
            context["next_url"] = next_url
            context["form_values"]["email"] = email

            if not email or not password:
                context["auth_error"] = "Vui lòng điền đầy đủ thông tin."
            elif password != password_confirm:
                context["auth_error"] = "Mật khẩu xác nhận không khớp."
            elif get_user_by_email(email):
                context["auth_error"] = "Email đã được sử dụng."
            else:
                user = User.objects.create_user(
                    username=build_unique_username_from_email(email),
                    password=password,
                    email=email,
                    is_active=False,
                )
                user.avatar = DEFAULT_AVATAR
                user.save()

                try:
                    send_account_activation_email(request, user)
                except Exception:
                    user.delete()
                    context["auth_error"] = "Không thể gửi email xác nhận. Vui lòng thử lại sau."
                    return render(request, "vecuatoi.html", context)

                context["auth_mode"] = "login"
                context["form_values"] = {
                    "email": "",
                }
                context["auth_success"] = "Đăng ký thành công. Vui lòng kiểm tra email để kích hoạt tài khoản trước khi đăng nhập."

    return render(request, "vecuatoi.html", context)


# USER PAGE
def user_page(request):
    return render(request, "userpage.html")


# MY EVENTS PAGE (CẤM XÓA)
def my_events(request):
    return render(request, "sukiencuatoi.html")

# SEARCH
def search(request):
    query = request.GET.get("query", "").lower()
    location = request.GET.get("location", "")
    date = request.GET.get("date", "")
    categories = request.GET.getlist("category")

    price_min = int(request.GET.get("priceMin", 0))

    price_max = request.GET.get("priceMax")
    if price_max:
        price_max = int(price_max)
    else:
        price_max = None

    events = Event.objects.all()

    # FILTER
    if query:
        events = events.filter(name__icontains=query)

    if location:
        events = events.filter(venue__city__icontains=location)

    if date:
        events = events.filter(date=date)

    if categories:
        events = events.filter(categories__slug__in=categories).distinct()

    filtered_events = []
    for event in events:
        min_price = event.min_price or 0
        max_price_event = event.max_price or 0

        if price_min and max_price_event < price_min:
            continue

        if price_max and min_price > price_max:
            continue

        filtered_events.append(event)

    # FILTER RESULTS
    results = {}
    for event in filtered_events:
        results[event.slug] = {
            "ten": event.name,
            "anh": event.image,
            "giaMin": float(event.min_price) if event.min_price else 0,
            "displayDate": event.date.strftime("%d.%m.%Y"),
            "startTime": event.start_time.strftime("%H:%M") if event.start_time else "",
            "endTime": event.end_time.strftime("%H:%M") if event.end_time else "",
            "categories": [c.slug for c in event.categories.all()]
        }

    # FRONTEND
    output = {
        "query": query,
        "locations": Venue.objects.values_list("city", flat=True).distinct(),
        "categories": Category.objects.all(),
        "selected_categories": categories,
        "location": location,
        "date": date,
        "price_ceiling": max(
            (e.max_price or 0 for e in Event.objects.all()),
            default=0
        ),
        "priceMin": price_min,
        "priceMax": price_max,
        "search_results": json.dumps(results)
    }

    return render(request, "search.html", output)