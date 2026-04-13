from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth import get_user_model
import uuid
import os

from users.services.avatar_service import process_avatar_upload

User = get_user_model()

# UPLOAD AVATAR
from users.services.avatar_service import process_avatar_upload

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_upload_avatar(request):
    try:
        file = request.FILES.get("avatar")

        avatar_url = process_avatar_upload(request.user, file)

        return Response({
            "success": True,
            "avatar": avatar_url
        })

    except ValueError as e:
        return Response({"error": str(e)}, status=400)

# CHANGE USERNAME
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def api_update_username(request):
    user = request.user
    username = request.data.get("username", "").strip().lower()

    if not username:
        return Response({"error": "Username cannot be empty"}, status=400)

    if User.objects.filter(username=username).exclude(id=user.id).exists():
        return Response({"error": "Username already taken"}, status=400)

    user.username = username
    user.save()

    return Response({
        "success": True,
        "username": username
    })

# CHANGE PASSWORD
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    user = request.user

    current = request.data.get("current_password")
    new = request.data.get("new_password")
    confirm = request.data.get("confirm_password")

    if not user.check_password(current):
        return Response({"error": "Sai mật khẩu hiện tại"}, status=400)

    if new != confirm:
        return Response({"error": "Mật khẩu xác nhận không khớp"}, status=400)

    if len(new) < 6:
        return Response({"error": "Mật khẩu quá ngắn"}, status=400)

    user.set_password(new)
    user.save()

    return Response({"success": True})