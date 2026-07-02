from rest_framework import serializers

from apps.auths.group.api.serializers import GroupSerializer
from apps.auths.permission.api.serializers import PermissionSerializer
from apps.models.user.models import User
from utils.auth import validate_password_strength


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    user_permissions = PermissionSerializer(many=True, read_only=True)
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)

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
            "gender_display",
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
            validate_password_strength(password, user=self.instance)
        return password

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


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
        validate_password_strength(password)
        return password

    def validate_accepted_terms(self, value):
        if value is not True:
            raise serializers.ValidationError(
                "Debe aceptar los términos y condiciones."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
