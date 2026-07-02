from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_password_strength(password, user=None):
    try:
        validate_password(password, user=user)
    except ValidationError as exc:
        raise serializers.ValidationError(list(exc.messages))
