from django.contrib.auth.models import Group
from rest_framework import serializers

from apps.auths.permission.api.serializers import PermissionSerializer


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = ("name", "permissions")
