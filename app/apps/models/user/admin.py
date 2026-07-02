from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "paternal_last_name",
        "maternal_last_name",
        "gender",
        "accepted_terms",
        "created",
        "modified",
    )
    list_per_page = 15
    search_fields = (
        "id",
        "username",
        "email",
        "first_name",
        "paternal_last_name",
        "maternal_last_name",
    )
    ordering = ("-created", "-modified")
    date_hierarchy = "created"
    list_filter = ("gender", "accepted_terms", "is_staff", "is_superuser", "is_active")
    filter_horizontal = ("groups", "user_permissions")

    fieldsets = (
        ("Credentials", {"fields": ("username", "password")}),
        (
            "Personal information",
            {
                "fields": (
                    "email",
                    "first_name",
                    "paternal_last_name",
                    "maternal_last_name",
                    "gender",
                    "phone",
                    "address",
                    "accepted_terms",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
        ("Custom dates", {"fields": ("created", "modified")}),
    )

    readonly_fields = ("created", "modified", "last_login")

    add_fieldsets = (
        (
            "Create user",
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "paternal_last_name",
                    "maternal_last_name",
                    "gender",
                    "phone",
                    "address",
                    "accepted_terms",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )