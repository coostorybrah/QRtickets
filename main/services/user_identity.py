import re

from django.contrib.auth import get_user_model


User = get_user_model()


def normalize_email(email):
    return (email or "").strip().lower()


def get_user_by_email(email):
    normalized = normalize_email(email)
    if not normalized:
        return None
    return User.objects.filter(email__iexact=normalized).first()


def build_unique_username_from_email(email):
    local_part = normalize_email(email).split("@")[0]
    base = re.sub(r"[^a-z0-9._-]", "", local_part) or "user"
    candidate = base[:150]
    index = 1

    while User.objects.filter(username=candidate).exists():
        suffix = f"_{index}"
        candidate = f"{base[:150 - len(suffix)]}{suffix}"
        index += 1

    return candidate