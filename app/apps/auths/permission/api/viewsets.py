from django.db.models import Q
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core.swagger_schemas import r401_no_token

from . import serializers

_TAG = ["Permisos"]

_permissions_list_200 = openapi.Response(
    description="**200 OK** — Lista de permisos disponibles en el sistema.",
    schema=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="user | user | Can add user",
                ),
                "name_es": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Nombre del permiso en español",
                    example="Puede Registrar user",
                ),
                "model_es": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Nombre del modelo al que aplica",
                    example="user",
                ),
                "codename": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="add_user",
                ),
                "content_type": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
                "action": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Acción normalizada (create | read | update | delete)",
                    example="create",
                ),
                "subject": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Modelo sobre el que aplica el permiso",
                    example="User",
                ),
            },
        ),
    ),
)


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_id="permissions_list",
        operation_summary="Listar permisos",
        operation_description=(
            "Devuelve todos los permisos de modelos de negocio registrados en el sistema.\n\n"
            "Se excluyen automáticamente los permisos internos de Django "
            "(`LogEntry`, `Session`, `ContentType`) y los de simplejwt "
            "(`BlacklistedToken`, `OutstandingToken`).\n\n"
            "Útil para construir interfaces de asignación de roles/permisos."
        ),
        responses={
            200: _permissions_list_200,
            401: r401_no_token,
        },
        tags=_TAG,
    ),
)
class PermissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.PermissionSerializer
    http_method_names = ["get"]
    queryset = serializers.Permission.objects.exclude(
        Q(codename__icontains="Logentry")
        | Q(codename__icontains="session")
        | Q(codename__icontains="contenttype")
        | Q(codename__icontains="Blacklistedtoken")
        | Q(codename__icontains="Outstandingtoken")
    )
