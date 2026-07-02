from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, viewsets

from core.swagger_schemas import (
    r400_validation,
    r401_no_token,
    r403_forbidden,
    r404_not_found,
)
from utils.permissions import FullModelPermissions

from .. import models
from . import serializers

_TAG = ["Usuarios"]

# ─── Shared response objects specific to this viewset ─────────────────────────

_user_detail_200 = openapi.Response(
    description="**200 OK** — Datos del usuario.",
    schema=serializers.UserSerializer(),
)

_user_created_201 = openapi.Response(
    description="**201 Created** — Usuario registrado exitosamente.",
    schema=serializers.UserRegisterSerializer(),
)

_user_list_item_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        "username": openapi.Schema(type=openapi.TYPE_STRING),
        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
        "paternal_last_name": openapi.Schema(type=openapi.TYPE_STRING),
        "maternal_last_name": openapi.Schema(type=openapi.TYPE_STRING),
        "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        "gender": openapi.Schema(type=openapi.TYPE_STRING, example="Masculino"),
        "phone": openapi.Schema(type=openapi.TYPE_STRING),
        "address": openapi.Schema(type=openapi.TYPE_STRING),
        "accepted_terms": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "created": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        "modified": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        "groups": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
        "user_permissions": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_OBJECT),
        ),
    },
)

_user_list_200 = openapi.Response(
    description="**200 OK** — Lista paginada de usuarios.",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "count": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Total de registros en la base de datos",
                example=42,
            ),
            "num_pages": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Número total de páginas",
                example=5,
            ),
            "page_number": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Página actual",
                example=1,
            ),
            "page_size": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Registros por página (máx. 1000)",
                example=10,
            ),
            "next": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="URL de la siguiente página",
                nullable=True,
                example="http://localhost:8000/api/users/?page=2",
            ),
            "previous": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="URL de la página anterior",
                nullable=True,
                example=None,
            ),
            "results": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="Lista de usuarios en esta página",
                items=_user_list_item_schema,
            ),
        },
    ),
    examples={
        "application/json": {
            "count": 1,
            "num_pages": 1,
            "page_number": 1,
            "page_size": 10,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": "9fdde656-45fc-4f1c-bd0f-86448e63b96e",
                    "username": "jdoe",
                    "first_name": "Juan",
                    "paternal_last_name": "Pérez",
                    "maternal_last_name": "García",
                    "email": "juan@example.com",
                    "gender": "Masculino",
                    "phone": "999888777",
                    "address": "Lima",
                    "accepted_terms": True,
                    "is_active": True,
                    "created": "2026-04-01T10:00:00Z",
                    "modified": "2026-04-01T10:00:00Z",
                    "groups": [],
                    "user_permissions": [],
                }
            ],
        }
    },
)

_user_deleted_204 = openapi.Response(
    description="**204 No Content** — Usuario eliminado exitosamente. Sin cuerpo de respuesta.",
)


# ─── ViewSet ──────────────────────────────────────────────────────────────────


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_id="users_list",
        operation_summary="Listar usuarios",
        operation_description=(
            "Devuelve una lista paginada de usuarios.\n\n"
            "**Parámetros de query:**\n"
            "- `search` — busca en `username`, `email`, `first_name`, "
            "`paternal_last_name` y `maternal_last_name`\n"
            "- `gender` — filtra por género (`M`, `F`, `O`)\n"
            "- `accepted_terms` — filtra por aceptación de términos (`true` o `false`)\n"
            "- `ordering` — ordena por `created`, `modified`, `email`, `first_name`\n"
            "- `page` — número de página\n"
            "- `page_size` — registros por página (máx. 1000, por defecto 10)"
        ),
        responses={
            200: _user_list_200,
            401: r401_no_token,
            403: r403_forbidden,
        },
        tags=_TAG,
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_id="users_create",
        operation_summary="Crear usuario",
        operation_description=(
            "Registra un nuevo usuario en el sistema.\n\n"
            "**Permisos requeridos:** `add_user`"
        ),
        responses={
            201: _user_created_201,
            400: r400_validation,
            401: r401_no_token,
            403: r403_forbidden,
        },
        tags=_TAG,
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_id="users_retrieve",
        operation_summary="Obtener usuario",
        operation_description=(
            "Devuelve los datos completos de un usuario por su `id` (UUID).\n\n"
            "**Permisos requeridos:** `view_user`"
        ),
        responses={
            200: _user_detail_200,
            401: r401_no_token,
            403: r403_forbidden,
            404: r404_not_found,
        },
        tags=_TAG,
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        operation_id="users_update",
        operation_summary="Actualizar usuario (completo)",
        operation_description=(
            "Reemplaza **todos** los campos editables de un usuario.\n\n"
            "Todos los campos requeridos deben enviarse. Para actualizar solo algunos campos "
            "usa `PATCH /api/users/{id}/`.\n\n"
            "**Permisos requeridos:** `change_user`"
        ),
        responses={
            200: _user_detail_200,
            400: r400_validation,
            401: r401_no_token,
            403: r403_forbidden,
            404: r404_not_found,
        },
        tags=_TAG,
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        operation_id="users_partial_update",
        operation_summary="Actualizar usuario (parcial)",
        operation_description=(
            "Actualiza uno o más campos de un usuario.\n\n"
            "Solo se requieren los campos que se desean modificar. "
            "Los campos omitidos conservan su valor actual.\n\n"
            "**Permisos requeridos:** `change_user`"
        ),
        responses={
            200: _user_detail_200,
            400: r400_validation,
            401: r401_no_token,
            403: r403_forbidden,
            404: r404_not_found,
        },
        tags=_TAG,
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_id="users_destroy",
        operation_summary="Eliminar usuario",
        operation_description=(
            "Elimina permanentemente un usuario del sistema.\n\n"
            "⚠️ Esta operación **no se puede deshacer**.\n\n"
            "**Permisos requeridos:** `delete_user`"
        ),
        responses={
            204: _user_deleted_204,
            401: r401_no_token,
            403: r403_forbidden,
            404: r404_not_found,
        },
        tags=_TAG,
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [FullModelPermissions]
    serializer_class = serializers.UserSerializer
    http_method_names = ["post", "get", "patch", "put", "delete"]
    pagination_class = serializers.CustomPagination
    queryset = models.User.objects.all().order_by("email")

    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    )

    search_fields = [
        "username",
        "email",
        "first_name",
        "paternal_last_name",
        "maternal_last_name",
    ]

    filterset_fields = [
        "gender",
        "accepted_terms",
        "is_active",
    ]

    ordering_fields = [
        "created",
        "modified",
        "email",
        "first_name",
        "username",
    ]

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.UserRegisterSerializer
        if self.action in ("update", "partial_update"):
            return serializers.UserUpdateSerializer
        return self.serializer_class