from django.http import JsonResponse
import uuid
import os

def api_upload_avatar(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    file = request.FILES.get("avatar")

    if not file:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    if not file.content_type.startswith("image/"):
        return JsonResponse({"error": "Invalid file type"}, status=400)

    if file.size > 2 * 1024 * 1024:
        return JsonResponse({"error": "File too large (max 2MB)"}, status=400)

    user = request.user

    if user.avatar and user.avatar.name != "avatars/default-avatar.png":
        user.avatar.delete(save=False)

    ext = os.path.splitext(file.name)[1]
    file.name = f"{uuid.uuid4()}{ext}"
    
    user.avatar = file
    user.save()

    return JsonResponse({
        "success": True,
        "avatar": user.avatar.url
    })