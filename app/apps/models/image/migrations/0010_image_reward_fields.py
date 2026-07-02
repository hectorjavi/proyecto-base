"""
Add reward fields directly to Image, replacing the separate ImageReward table.
Depends on reward 0005 so the FK targets already exist.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("image", "0009_remove_image_image_validation_message_and_more"),
        ("reward", "0005_rewardwithdrawal_imagereward_withdrawal"),
    ]

    operations = [
        migrations.AddField(
            model_name="image",
            name="reward_withdrawal",
            field=models.ForeignKey(
                blank=True,
                help_text="Retiro al que pertenece la recompensa de esta imagen.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="images",
                to="reward.rewardwithdrawal",
                verbose_name="Retiro de recompensa",
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="reward_rule",
            field=models.ForeignKey(
                blank=True,
                help_text="Regla que determinó el monto de recompensa para esta imagen.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="images",
                to="reward.rewardrule",
                verbose_name="Regla de recompensa aplicada",
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="reward_amount",
            field=models.DecimalField(
                blank=True,
                decimal_places=8,
                help_text="Monto en soles otorgado por esta imagen. Null si aún no se cobró.",
                max_digits=18,
                null=True,
                verbose_name="Monto de recompensa (soles)",
            ),
        ),
        migrations.AddField(
            model_name="image",
            name="reward_claimed_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Fecha y hora en que se cobró la recompensa. Null si aún no se cobró.",
                null=True,
                verbose_name="Fecha de cobro de recompensa",
            ),
        ),
    ]
