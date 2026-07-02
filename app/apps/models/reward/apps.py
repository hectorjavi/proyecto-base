from django.apps import AppConfig


class RewardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.models.reward"
    verbose_name = "Recompensas"

    def ready(self):
        __import__("apps.models.reward.signals")
