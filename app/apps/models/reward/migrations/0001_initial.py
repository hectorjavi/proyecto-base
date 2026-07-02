import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("image", "0009_remove_image_image_validation_message_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RewardRule",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Etiqueta descriptiva de la regla (ejemplo: 'Score alto').",
                        max_length=100,
                        verbose_name="Nombre",
                    ),
                ),
                (
                    "score_min",
                    models.FloatField(
                        help_text="Valor mínimo de score (inclusivo) para aplicar esta regla.",
                        verbose_name="Score mínimo",
                    ),
                ),
                (
                    "score_max",
                    models.FloatField(
                        help_text="Valor máximo de score (inclusivo) para aplicar esta regla.",
                        verbose_name="Score máximo",
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="Monto en soles que se otorga al usuario cuando su imagen cae en este rango.",
                        max_digits=14,
                        verbose_name="Monto (soles)",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Solo las reglas activas se consideran al cobrar una recompensa.",
                        verbose_name="Activa",
                    ),
                ),
            ],
            options={
                "verbose_name": "Regla de recompensa",
                "verbose_name_plural": "Reglas de recompensa",
                "db_table": "reward_rules",
                "ordering": ["score_min"],
                "indexes": [
                    models.Index(fields=["is_active"], name="reward_rule_is_acti_idx"),
                    models.Index(fields=["score_min", "score_max"], name="reward_rule_score_m_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="UserRewardBalance",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        decimal_places=4,
                        default=0,
                        help_text="Suma acumulada de todas las recompensas cobradas por el usuario.",
                        max_digits=16,
                        verbose_name="Saldo total (soles)",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        help_text="Usuario dueño del saldo.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reward_balance",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Saldo de recompensas",
                "verbose_name_plural": "Saldos de recompensas",
                "db_table": "user_reward_balances",
            },
        ),
        migrations.CreateModel(
            name="ImageReward",
            fields=[
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "id",
                    model_utils.fields.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=4,
                        help_text="Snapshot del monto en soles al momento del cobro.",
                        max_digits=14,
                        verbose_name="Monto cobrado (soles)",
                    ),
                ),
                (
                    "claimed_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Fecha de cobro",
                    ),
                ),
                (
                    "image",
                    models.OneToOneField(
                        help_text="Imagen por la que se cobró la recompensa.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reward",
                        to="image.image",
                        verbose_name="Imagen",
                    ),
                ),
                (
                    "reward_rule",
                    models.ForeignKey(
                        help_text="Regla de recompensa que se aplicó al momento del cobro.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="image_rewards",
                        to="reward.rewardrule",
                        verbose_name="Regla aplicada",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="Usuario que cobró la recompensa.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="image_rewards",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Recompensa de imagen",
                "verbose_name_plural": "Recompensas de imágenes",
                "db_table": "image_rewards",
                "ordering": ["-claimed_at"],
                "indexes": [
                    models.Index(fields=["user"], name="image_rewar_user_id_idx"),
                    models.Index(fields=["claimed_at"], name="image_rewar_claime_idx"),
                ],
            },
        ),
    ]
