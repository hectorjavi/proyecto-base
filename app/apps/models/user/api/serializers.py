from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from apps.auths.group.api.serializers import GroupSerializer
from apps.auths.permission.api.serializers import PermissionSerializer
from apps.models.user.models import User
from utils.api.pagination import CustomPagination  # noqa: F401


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    user_permissions = PermissionSerializer(many=True, read_only=True)
    gender = serializers.CharField(source="get_gender_display", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "paternal_last_name",
            "maternal_last_name",
            "email",
            "gender",
            "phone",
            "address",
            "accepted_terms",
            "is_active",
            "created",
            "modified",
            "groups",
            "user_permissions",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "paternal_last_name",
            "maternal_last_name",
            "email",
            "gender",
            "phone",
            "address",
            "accepted_terms",
            "password",
        )
        read_only_fields = ("id",)

    def validate_password(self, password):
        if password:
            password = make_password(password)
        return password


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    accepted_terms = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "first_name",
            "paternal_last_name",
            "maternal_last_name",
            "email",
            "gender",
            "phone",
            "address",
            "accepted_terms",
            "created",
            "modified",
        )
        read_only_fields = ("id", "created", "modified")

    def validate_password(self, password):
        return make_password(password)

    def validate_accepted_terms(self, value):
        if value is not True:
            raise serializers.ValidationError(
                "Debe aceptar los términos y condiciones."
            )
        return value
