import os

from django.conf import settings
from django.contrib.auth.models import Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .apps import UserConfig
from .models import User


def create_default_user():
    user, created = User.objects.get_or_create(
        email="test@gmail.com",
        defaults={
            "username": "test",
            "first_name": "Test",
            "paternal_last_name": "User",
            "maternal_last_name": "Default",
            "accepted_terms": True,
            "is_superuser": True,
            "is_staff": True,
        },
    )

    if created:
        user.set_password("test")
        all_permissions = Permission.objects.all()
        user.user_permissions.set(all_permissions)
        user.save()


@receiver(post_migrate)
def create(sender, **kwargs):
    if not isinstance(sender, UserConfig):
        return
    if not (settings.DEBUG or os.environ.get("CREATE_DEFAULT_SUPERUSER") == "1"):
        return
    create_default_user()
