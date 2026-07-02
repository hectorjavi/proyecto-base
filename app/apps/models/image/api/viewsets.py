from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from core.swagger_schemas import (
    r400_validation,
    r401_no_token,
    r403_forbidden,
    r404_not_found,
)
from utils.permissions import FullModelPermissions

from .. import models
from . import serializers
from .filters import ImageFilter

_TAG = ["Imágenes"]

# ─── Shared response objects ──────────────────────────────────────────────────

_image_list_item_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        "user": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        "file": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI),
        "file_name": openapi.Schema(type=openapi.TYPE_STRING),
        "file_extension": openapi.Schema(type=openapi.TYPE_STRING, example=".jpg"),
        "device_type": openapi.Schema(type=openapi.TYPE_STRING, example="mobile"),
        "image_score": openapi.Schema(type=openapi.TYPE_NUMBER, format="float", x_nullable=True),
        "is_reward_claimed": openapi.Schema(type=openapi.TYPE_BOOLEAN),
        "reward_amount": openapi.Schema(type=openapi.TYPE_STRING, x_nullable=True),
        "reward_claimed_at": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATETIME,
            x_nullable=True,
        ),
        "uploaded_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        "created": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        "modified": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
    },
)

_image_list_200 = openapi.Response(
    description="**200 OK** — Lista paginada de imágenes del usuario autenticado.",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "count": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Total de registros.",
                example=42,
            ),
            "num_pages": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Número total de páginas.",
                example=5,
            ),
            "page_number": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Página actual.",
                example=1,
            ),
            "page_size": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="Registros por página (máx. 1000, por defecto 10).",
                example=10,
            ),
            "next": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="URL de la siguiente página (null si es la última).",
                nullable=True,
                example="http://localhost:8000/api/images/?page=2",
            ),
            "previous": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="URL de la página anterior (null si es la primera).",
                nullable=True,
                example=None,
            ),
            "results": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                description="Lista de imágenes en esta página.",
                items=_image_list_item_schema,
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
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "user": "4a1b1d8f-2b3c-4d5e-8f90-a1b2c3d4e5f6",
                    "file": "https://res.cloudinary.com/demo/image/upload/v1/images/2026/04/01/img.jpg",
                    "file_name": "img_001.jpg",
                    "file_extension": ".jpg",
                    "device_type": "mobile",
                    "image_score": 0.82,
                    "is_reward_claimed": True,
                    "reward_amount": "0.00500000",
                    "reward_claimed_at": "2026-04-01T13:20:00Z",
                    "uploaded_at": "2026-04-01T13:10:00Z",
                    "created": "2026-04-01T13:10:00Z",
                    "modified": "2026-04-01T13:20:00Z",
                }
            ],
        }
    },
)

_image_detail_200 = openapi.Response(
    description="**200 OK** — Datos completos de la imagen.",
    schema=serializers.ImageSerializer(),
)

_image_created_201 = openapi.Response(
    description="**201 Created** — Imagen creada exitosamente.",
    schema=serializers.ImageSerializer(),
)

_image_deleted_204 = openapi.Response(
    description="**204 No Content** — Imagen eliminada exitosamente. Sin cuerpo de respuesta.",
)

_upload_base64_created_201 = openapi.Response(
    description="**201 Created** — Imagen creada exitosamente a partir del base64.",
    schema=serializers.ImageSerializer(),
)

# ─── ViewSet ──────────────────────────────────────────────────────────────────


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_id="images_list",
        operation_summary="Listar imágenes",
        operation_description=(
            "Devuelve una lista paginada de imágenes subidas por el usuario autenticado.\n\n"
            "**Parámetros de query:**\n"
            "- `search` — busca en `file_name`, `file_extension`, `device_brand`, `device_model`\n"
            "- `device_type` — filtra por tipo de dispositivo (`mobile`, `desktop`, `tablet`, `unknown`)\n"
            "- `file_extension` — filtra por extensión (`.jpg`, `.png`, etc.)\n"
            "- `ordering` — ordena por `created`, `modified`, `uploaded_at`, `captured_at` "
            "(prefijo `-` para descendente)\n"
            "- `page` — número de página\n"
            "- `page_size` — registros por página (máx. 1000, por defecto 10)\n\n"
            "**Permisos requeridos:** `view_image`"
        ),
        responses={
            200: _image_list_200,
            401: r401_no_token,
            403: r403_forbidden,
        },
        tags=_TAG,
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_id="images_create",
        operation_summary="Subir imagen (multipart)",
        operation_description=(
            "Sube una imagen mediante `multipart/form-data`.\n\n"
            "El campo `file` es obligatorio. Los demás campos (metadatos de dispositivo, "
            "IP, fecha de captura, etc.) son opcionales.\n\n"
            "Los campos `file_name` y `file_extension` se calculan automáticamente.\n"
            "Si la imagen supera 1500px en su lado mayor, se redimensiona antes de guardarse.\n\n"
            "**Permisos requeridos:** `add_image`"
        ),
        responses={
            201: _image_created_201,
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
        operation_id="images_retrieve",
        operation_summary="Obtener imagen",
        operation_description=(
            "Devuelve los datos completos de una imagen por su `id` (UUID).\n\n"
            "Solo se puede acceder a imágenes propias del usuario autenticado.\n\n"
            "**Permisos requeridos:** `view_image`"
        ),
        responses={
            200: _image_detail_200,
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
        operation_id="images_update",
        operation_summary="Actualizar imagen (completo)",
        operation_description=(
            "Reemplaza **todos** los campos editables de una imagen.\n\n"
            "Para actualizar solo algunos campos usa `PATCH /api/images/{id}/`.\n\n"
            "**Permisos requeridos:** `change_image`"
        ),
        responses={
            200: _image_detail_200,
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
        operation_id="images_partial_update",
        operation_summary="Actualizar imagen (parcial)",
        operation_description=(
            "Actualiza uno o más campos de una imagen.\n\n"
            "Solo se requieren los campos que se desean modificar. "
            "Los campos omitidos conservan su valor actual.\n\n"
            "**Permisos requeridos:** `change_image`"
        ),
        responses={
            200: _image_detail_200,
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
        operation_id="images_destroy",
        operation_summary="Eliminar imagen",
        operation_description=(
            "Elimina permanentemente una imagen y su archivo en el storage (Cloudinary).\n\n"
            "Esta operación **no se puede deshacer**.\n\n"
            "**Permisos requeridos:** `delete_image`"
        ),
        responses={
            204: _image_deleted_204,
            401: r401_no_token,
            403: r403_forbidden,
            404: r404_not_found,
        },
        tags=_TAG,
    ),
)
class ImageViewSet(viewsets.ModelViewSet):
    permission_classes = [FullModelPermissions]
    serializer_class = serializers.ImageSerializer
    http_method_names = ["post", "get", "delete"]
    pagination_class = serializers.CustomPagination
    queryset = models.Image.objects.filter().order_by("-uploaded_at")
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    search_fields = ["file_name", "file_extension", "device_brand", "device_model"]
    filterset_class = ImageFilter
    ordering_fields = ["created", "modified", "uploaded_at", "captured_at"]
    ordering = ["-uploaded_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return models.Image.objects.none()
        if self.request.method == 'DELETE':
            return (
                models.Image.objects.filter(
                    user=self.request.user,
                    reward_withdrawal__isnull=True
                )
                .prefetch_related("image_tags__tag")
            )
        else:
            return (
                models.Image.objects.filter(user=self.request.user)
                .prefetch_related("image_tags__tag")
            )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        method="post",
        operation_id="images_claim_reward",
        operation_summary="Cobrar recompensa de una imagen",
        operation_description=(
            "Cobra la recompensa en soles para una imagen según su `image_score`.\n\n"
            "**Reglas de negocio:**\n"
            "- La imagen debe pertenecer al usuario autenticado.\n"
            "- La imagen debe tener `image_score` registrado.\n"
            "- La imagen no puede haber cobrado recompensa previamente.\n"
            "- Debe existir una regla activa cuyo rango incluya el `image_score`.\n\n"
            "En caso de éxito, se crea el registro de cobro y se actualiza el saldo acumulado del usuario.\n\n"
            "**Permisos requeridos:** `view_image`"
        ),
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT),
        responses={
            201: openapi.Response(
                description="**201 Created** — Recompensa cobrada exitosamente.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                        "image": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                        "reward_rule": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                        "reward_rule_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "amount": openapi.Schema(type=openapi.TYPE_STRING, description="Monto en soles"),
                        "claimed_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                    },
                ),
            ),
            400: r400_validation,
            401: r401_no_token,
            403: r403_forbidden,
            404: r404_not_found,
        },
        tags=_TAG,
    )
    @action(detail=True, methods=["post"], url_path="claim")
    def claim_reward(self, request, pk=None):
        """Cobra la recompensa de una imagen según su image_score."""
        from django.utils import timezone
        from apps.models.reward.models import RewardRule, RewardWithdrawal

        image = self.get_object()

        if image.image_score is None:
            raise ValidationError(
                {"detail": "La imagen no tiene image_score registrado. No es posible cobrar recompensa."}
            )

        if image.is_reward_claimed:
            raise ValidationError(
                {"detail": "Esta imagen ya tiene una recompensa cobrada."}
            )

        rule = (
            RewardRule.objects.filter(
                is_active=True,
                score_min__lte=image.image_score,
                score_max__gte=image.image_score,
            )
            .order_by("-amount")
            .first()
        )

        if rule is None:
            raise ValidationError(
                {
                    "detail": (
                        f"No existe una regla activa para el score {image.image_score:.4f}. "
                        "Contacta al administrador."
                    )
                }
            )

        with transaction.atomic():
            withdrawal = (
                RewardWithdrawal.objects
                .select_for_update()
                .filter(user=request.user, is_paid=False)
                .first()
            )
            if withdrawal is None:
                withdrawal = RewardWithdrawal.objects.create(
                    user=request.user,
                    total_amount=Decimal("0"),
                )

            image.reward_withdrawal = withdrawal
            image.reward_rule = rule
            image.reward_amount = rule.amount
            image.reward_claimed_at = timezone.now()
            image.save(
                update_fields=["reward_withdrawal", "reward_rule", "reward_amount", "reward_claimed_at", "modified"]
            )

            RewardWithdrawal.objects.filter(pk=withdrawal.pk).update(
                total_amount=F("total_amount") + rule.amount
            )

        return Response(
            {
                "id": str(image.pk),
                "reward_rule": str(rule.pk),
                "reward_rule_name": rule.name,
                "reward_amount": str(image.reward_amount),
                "reward_claimed_at": image.reward_claimed_at,
                "reward_withdrawal": str(withdrawal.pk),
            },
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        method="post",
        operation_id="images_upload_base64",
        operation_summary="Subir imagen en base64",
        operation_description=(
            "Crea una imagen a partir del campo `image_base64`.\n\n"
            "Acepta tanto base64 puro como formato data URL:\n"
            "`data:image/jpeg;base64,<contenido>`\n\n"
            "Formatos soportados: `jpg`, `png`, `webp`, `gif`.\n"
            "Si la imagen supera 1500px en su lado mayor, se redimensiona automáticamente.\n\n"
            "**Permisos requeridos:** `add_image`"
        ),
        request_body=serializers.ImageBase64UploadSerializer,
        responses={
            201: _upload_base64_created_201,
            400: r400_validation,
            401: r401_no_token,
            403: r403_forbidden,
        },
        tags=_TAG,
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="upload-base64",
    )
    def upload_base64(self, request):
        serializer = serializers.ImageBase64UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.save(user=request.user)
        response_serializer = serializers.ImageSerializer(
            image, context=self.get_serializer_context()
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
