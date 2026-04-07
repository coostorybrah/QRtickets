from django.db.models import Q
from django.contrib.auth import authenticate, get_user_model

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# ĐĂNG KÝ
@api_view(["POST"])
@permission_classes([AllowAny])
def api_signup(request):
    data = request.data

    username = data.get("username", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password")

    if not username or not email or not password:
        return Response({"error": "Missing fields"}, status=400)

    if len(password) < 6:
        return Response({"error": "Password too short"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=400)

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
    )

    return Response({
        "success": True,
        "message": "Đăng kí thành công!"
    })


# ĐĂNG NHẬP
@api_view(["POST"])
@permission_classes([AllowAny])
def api_login(request):
    data = request.data

    identifier = data.get("username")
    identifier = identifier.strip().lower()
    password = data.get("password")

    user_obj = User.objects.filter(
        Q(username=identifier) | Q(email=identifier)
    ).first()

    if not user_obj:
        return Response({"error": "Invalid credentials"}, status=401)

    user = authenticate(username=user_obj.username, password=password)

    if not user:
        return Response({"error": "Invalid credentials"}, status=401)

    # ✅ Generate JWT
    refresh = RefreshToken.for_user(user)

    return Response({
        "success": True,
        "loggedIn": True,
        "access": str(refresh.access_token),
        "refresh": str(refresh),

        "avatar": user.avatar.url if user.avatar else None,
        "username": user.username,
        "is_organizer": hasattr(user, "organizer"),
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "email": user.email
    })

# KIỂM TRA LOGIN
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_me(request):
    user = request.user

    return Response({
        "loggedIn": True,
        "avatar": user.avatar.url if user.avatar else None,
        "username": user.username,
        "is_organizer": hasattr(user, "organizer"),
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "email": user.email,
    })
