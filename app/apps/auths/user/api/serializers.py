from rest_framework import serializers

from apps.models.user.models import User


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

    def validate(self, data):
        if data["current_password"] == data["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "Enter a password different from the current one."}
            )
        return data