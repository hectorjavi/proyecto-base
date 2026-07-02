from django.contrib.auth.models import Permission
from rest_framework import serializers


class PermissionSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    name_es = serializers.SerializerMethodField()
    model_es = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = (
            "id",
            "name",
            "name_es",
            "model_es",
            "codename",
            "content_type",
            "action",
            "subject",
        )

    def get_name_es(self, fields):
        model_name = str(fields).split("|")[1].strip()
        action = str(fields).split("|")[2].strip().split()[1]
        actions_map = {
            "add": "Registrar",
            "view": "Consultar",
            "delete": "Eliminar",
            "change": "Modificar",
        }
        action = actions_map[action]
        name_es = f"Puede {action} {model_name}"
        return name_es

    def get_model_es(self, fields):
        model_name = str(fields).split("|")[1].strip()
        return model_name

    def get_subject(self, foo_instance):
        return foo_instance.codename.split("_")[1].capitalize()

    def get_action(self, foo_instance):
        action = foo_instance.codename.split("_")[0]
        if action == "add":
            return "create"
        elif action == "view":
            return "read"
        elif action == "change":
            return "update"
        elif action == "delete":
            return action
        return ""
