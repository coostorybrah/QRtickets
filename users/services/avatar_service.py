import os
import uuid
from io import BytesIO
from PIL import Image

from django.core.files.base import ContentFile


ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_SIZE_MB = 2


def validate_avatar(file):
    if not file:
        raise ValueError("No file uploaded")

    if file.content_type not in ALLOWED_TYPES:
        raise ValueError("Invalid file type")

    if file.size > MAX_SIZE_MB * 1024 * 1024:
        raise ValueError("File too large (max 2MB)")


def generate_filename(file):
    ext = os.path.splitext(file.name)[1].lower()
    return f"{uuid.uuid4()}{ext}"


def compress_avatar(file, max_size=(512, 512), quality=75):
    img = Image.open(file)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail(max_size)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=quality)

    return ContentFile(buffer.getvalue(), name="compressed.jpg")


def delete_old_avatar(user):
    if user.avatar:
        user.avatar.delete(save=False)


def process_avatar_upload(user, file):
    validate_avatar(file)

    delete_old_avatar(user)

    compressed = compress_avatar(file)
    compressed.name = generate_filename(file)

    user.avatar = compressed
    user.save()

    return user.avatar.url