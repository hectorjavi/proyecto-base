from rest_framework import serializers

from apps.models.user.models import User
from utils.auth import validate_password_strength


class UserMeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "paternal_last_name",
            "maternal_last_name",
            "gender",
            "phone",
            "address",
            "email",
            "accepted_terms",
        )
        read_only_fields = ("id",)


class UserMeUpdatePssSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        help_text="Current user password.",
        write_only=True,
    )
    new_password = serializers.CharField(
        help_text="New user password.",
        write_only=True,
    )

    def validate_new_password(self, value):
        user = self.context.get("request").user if self.context.get("request") else None
        validate_password_strength(value, user=user)
        return value

    def validate(self, data):
        if data["current_password"] == data["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "Enter a password different from the current one."}
            )
        return data
