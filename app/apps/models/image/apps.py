from django.apps import AppConfig


class ImageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.models.image"

    def ready(self):
        import apps.models.image.signals  # noqa: F401
