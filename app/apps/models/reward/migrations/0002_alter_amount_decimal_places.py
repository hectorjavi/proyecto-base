from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reward", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rewardrule",
            name="amount",
            field=models.DecimalField(
                decimal_places=4,
                max_digits=14,
                verbose_name="Monto (soles)",
                help_text="Monto en soles que se otorga al usuario cuando su imagen cae en este rango.",
            ),
        ),
        migrations.AlterField(
            model_name="imagereward",
            name="amount",
            field=models.DecimalField(
                decimal_places=4,
                max_digits=14,
                verbose_name="Monto cobrado (soles)",
                help_text="Snapshot del monto en soles al momento del cobro.",
            ),
        ),
        migrations.AlterField(
            model_name="userrewardbalance",
            name="total_amount",
            field=models.DecimalField(
                decimal_places=4,
                default=0,
                max_digits=16,
                verbose_name="Saldo total (soles)",
                help_text="Suma acumulada de todas las recompensas cobradas por el usuario.",
            ),
        ),
    ]
