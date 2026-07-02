from rest_framework import serializers

from apps.models.image.models import Image

from ..models import RewardRule, RewardWithdrawal


class RewardRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardRule
        fields = (
            "id",
            "name",
            "score_min",
            "score_max",
            "amount",
            "is_active",
            "created",
            "modified",
        )
        read_only_fields = ("id", "created", "modified")

    def validate(self, attrs):
        score_min = attrs.get("score_min", getattr(self.instance, "score_min", None))
        score_max = attrs.get("score_max", getattr(self.instance, "score_max", None))
        if score_min is not None and score_max is not None and score_min >= score_max:
            raise serializers.ValidationError(
                {"score_max": "score_max debe ser mayor que score_min."}
            )
        return attrs


class ImageRewardHistorySerializer(serializers.ModelSerializer):
    """Imagen con datos de su recompensa cobrada (historial por usuario)."""

    reward_rule_name = serializers.CharField(source="reward_rule.name", read_only=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "file",
            "file_name",
            "image_score",
            "reward_withdrawal",
            "reward_rule",
            "reward_rule_name",
            "reward_amount",
            "reward_claimed_at",
        )
        read_only_fields = fields


class RewardWithdrawalSerializer(serializers.ModelSerializer):
    """Retiro con resumen de cobros. El detalle completo usa RewardWithdrawalDetailSerializer."""

    images_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RewardWithdrawal
        fields = (
            "id",
            "user",
            "total_amount",
            "is_paid",
            "paid_at",
            "images_count",
            "created",
            "modified",
        )
        read_only_fields = fields


class RewardWithdrawalDetailSerializer(serializers.ModelSerializer):
    """Retiro con listado completo de imágenes incluidas."""

    images = ImageRewardHistorySerializer(many=True, read_only=True)
    images_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = RewardWithdrawal
        fields = (
            "id",
            "user",
            "total_amount",
            "is_paid",
            "paid_at",
            "images_count",
            "images",
            "created",
            "modified",
        )
        read_only_fields = fields


class RewardBalanceSerializer(serializers.Serializer):
    """Saldo calculado en tiempo real para el usuario autenticado."""

    user = serializers.UUIDField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=8, read_only=True)
    total_rewards = serializers.IntegerField(read_only=True)
