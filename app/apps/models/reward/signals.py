from decimal import Decimal

from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .apps import RewardConfig
from .models import RewardRule


# Reglas iniciales tras migrar el esquema (idempotente: update_or_create por nombre).
DEFAULT_REWARD_RULES: tuple[tuple[str, float, float, Decimal], ...] = (
    ("Regular", 0.2, 0.5, Decimal("0.05")),
    ("Bueno", 0.5, 0.7, Decimal("0.1")),
    ("Muy bueno", 0.7, 0.9, Decimal("0.2")),
    ("Excelente", 0.9, 1.0, Decimal("0.3")),
)

@receiver(post_migrate, dispatch_uid="apps.models.reward.seed_reward_rules")
def seed_default_reward_rules(sender, **kwargs):
    if not isinstance(sender, RewardConfig):
        return
    for name, score_min, score_max, amount in DEFAULT_REWARD_RULES:
        RewardRule.objects.update_or_create(
            name=name,
            defaults={
                "score_min": score_min,
                "score_max": score_max,
                "amount": amount,
                "is_active": True,
            },
        )
