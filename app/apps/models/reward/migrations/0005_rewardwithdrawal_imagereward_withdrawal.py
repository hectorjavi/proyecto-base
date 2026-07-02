import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reward", "0004_delete_userrewardbalance"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RewardWithdrawal",
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
                        decimal_places=8,
                        default=0,
                        help_text="Suma de los montos de todas las recompensas de imágenes en este retiro.",
                        max_digits=20,
                        verbose_name="Total acumulado (soles)",
                    ),
                ),
                (
                    "is_paid",
                    models.BooleanField(
                        default=False,
                        help_text="Indica si el usuario ya cobró este retiro. Una vez True no puede modificarse.",
                        verbose_name="Cobrado",
                    ),
                ),
                (
                    "paid_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Fecha y hora en que el usuario cobró este retiro.",
                        null=True,
                        verbose_name="Fecha de cobro",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="Usuario dueño del retiro.",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reward_withdrawals",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Usuario",
                    ),
                ),
            ],
            options={
                "verbose_name": "Retiro de recompensas",
                "verbose_name_plural": "Retiros de recompensas",
                "db_table": "reward_withdrawals",
                "ordering": ["-created"],
                "indexes": [
                    models.Index(fields=["user", "is_paid"], name="reward_with_user_id_is_paid_idx"),
                ],
            },
        ),
        migrations.AddField(
            model_name="imagereward",
            name="withdrawal",
            field=models.ForeignKey(
                blank=True,
                help_text="Retiro al que pertenece este cobro de imagen.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="image_rewards",
                to="reward.rewardwithdrawal",
                verbose_name="Retiro",
            ),
        ),
        migrations.AddIndex(
            model_name="imagereward",
            index=models.Index(fields=["withdrawal"], name="image_rewar_withdra_idx"),
        ),
    ]
