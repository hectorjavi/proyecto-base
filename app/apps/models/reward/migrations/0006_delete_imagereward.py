"""
Remove the ImageReward table. Its data is now stored directly on Image
via the reward_withdrawal / reward_rule / reward_amount / reward_claimed_at fields
added in image migration 0010.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reward", "0005_rewardwithdrawal_imagereward_withdrawal"),
        ("image", "0010_image_reward_fields"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ImageReward",
        ),
    ]
