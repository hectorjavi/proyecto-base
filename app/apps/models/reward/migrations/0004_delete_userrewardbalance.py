from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reward", "0003_alter_amount_8_decimal_places"),
    ]

    operations = [
        migrations.DeleteModel(
            name="UserRewardBalance",
        ),
    ]
