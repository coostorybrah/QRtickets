from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
import json

User = get_user_model()

DEFAULT_AVATAR = "avatars/default-avatar.png"


# ĐĂNG KÝ
def api_signup(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    # check tồn tại
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already exists"}, status=400)

    # tạo user
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
    )

    user.avatar = DEFAULT_AVATAR
    user.save()

    login(request, user)

    return JsonResponse({
        "success": True,
        "avatar": user.avatar.url if user.avatar else None,
        "username": user.username,
        "message": "Đăng kí thành công!"
    })


# ĐĂNG NHẬP
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)

    username = data.get("username")
    password = data.get("password")

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)

        return JsonResponse({
            "success": True,
            "avatar": user.avatar.url if user.avatar else None,
            "username": user.username
        })

    return JsonResponse({"error": "Invalid credentials"}, status=401)


# KIỂM TRA LOGIN
def api_me(request):
    if not request.user.is_authenticated:
        return JsonResponse({"loggedIn": False})

    return JsonResponse({
        "loggedIn": True,
        "avatar": request.user.avatar.url if request.user.avatar else None,
        "username": request.user.username
    })


# ĐĂNG XUẤT
def api_logout(request):
    logout(request)
    return JsonResponse({"success": True})