from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from main.services.account_activation import send_account_activation_email
from main.services.user_identity import (
    build_unique_username_from_email,
    get_user_by_email,
    normalize_email,
)
import json

User = get_user_model()

DEFAULT_AVATAR = "/static/images/avatars/default-avatar.png"


# ĐĂNG KÝ
@csrf_exempt
def api_signup(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Yêu cầu POST."}, status=400)

    data = json.loads(request.body)

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    email = normalize_email(data.get("email"))

    if not email or not password:
        return JsonResponse({"success": False, "message": "Vui lòng nhập đầy đủ thông tin."}, status=400)

    if get_user_by_email(email):
        return JsonResponse({"success": False, "message": "Email đã tồn tại."}, status=400)

    if not username:
        username = build_unique_username_from_email(email)
    elif User.objects.filter(username=username).exists():
        return JsonResponse({"success": False, "message": "Tên đăng nhập đã tồn tại."}, status=400)

    # tạo user
    user = User.objects.create_user(
        username=username,
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
        return JsonResponse(
            {"success": False, "message": "Không thể gửi email xác nhận. Vui lòng thử lại sau."},
            status=500,
        )

    return JsonResponse({
        "success": True,
        "requires_activation": True,
        "message": "Đăng ký thành công. Vui lòng kiểm tra email để kích hoạt tài khoản.",
    })


# ĐĂNG NHẬP
@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Yêu cầu POST."}, status=400)

    data = json.loads(request.body)

    email = normalize_email(data.get("email"))
    password = data.get("password")

    if not email or not password:
        return JsonResponse({"success": False, "message": "Vui lòng nhập email và mật khẩu."}, status=400)

    existing_user = get_user_by_email(email)
    if existing_user and not existing_user.is_active:
        return JsonResponse(
            {
                "success": False,
                "message": "Tài khoản chưa được kích hoạt. Vui lòng mở email và nhấn link xác nhận.",
            },
            status=403,
        )

    user = authenticate(request, username=existing_user.username if existing_user else "", password=password)

    if user is not None:
        login(request, user)

        return JsonResponse({
            "success": True,
            "avatar": user.avatar,
            "username": user.username
        })

    return JsonResponse({"success": False, "message": "Sai email hoặc mật khẩu."}, status=401)


# KIỂM TRA LOGIN
def api_me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"loggedIn": False})

    return JsonResponse({
        "loggedIn": True,
        "avatar": request.user.avatar,
        "username": request.user.username
    })


# ĐĂNG XUẤT
@csrf_exempt
def api_logout(request):
    logout(request)
    return JsonResponse({"success": True})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        return redirect("/my-tickets/?activated=1")

    return redirect("/my-tickets/?activated=0")