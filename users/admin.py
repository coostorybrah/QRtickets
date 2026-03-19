from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
	model = User
	list_display = ("email", "username", "is_active", "is_staff", "is_superuser")
	ordering = ("email",)
	search_fields = ("email", "username")
	readonly_fields = ("created_at",)

	fieldsets = UserAdmin.fieldsets + (
		("Thông tin bổ sung", {"fields": ("avatar", "created_at")}),
	)
