from decimal import Decimal

from django.db.models import Count, F, Sum
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.models.image.models import Image

from core.swagger_schemas import (
    r400_validation,
    r401_no_token,
    r404_not_found,
)

from ..models import RewardWithdrawal
from .serializers import (
    RewardBalanceSerializer,  # noqa: F401
    RewardWithdrawalDetailSerializer,
    RewardWithdrawalSerializer,
)

_TAG_BALANCE = ["Saldo de recompensas"]
_TAG_WITHDRAWALS = ["Retiros de recompensas"]

_withdrawals_list_200 = openapi.Response(
    description="**200 OK** — Lista de retiros (abiertos e históricos) del usuario autenticado.",
    schema=RewardWithdrawalSerializer(many=True),
    examples={
        "application/json": [
            {
                "id": "84195747-58d8-4638-938f-86dd8c690f2e",
                "user": "4a1b1d8f-2b3c-4d5e-8f90-a1b2c3d4e5f6",
                "total_amount": "0.01400000",
                "is_paid": False,
                "paid_at": None,
                "images_count": 4,
                "created": "2026-04-01T13:00:00Z",
                "modified": "2026-04-01T13:20:00Z",
            }
        ]
    },
)


# ─── RewardWithdrawalViewSet ──────────────────────────────────────────────────


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=_TAG_WITHDRAWALS,
        operation_id="reward_withdrawals_list",
        operation_summary="Listar retiros de recompensas",
        operation_description=(
            "Retorna todos los retiros del usuario autenticado (abiertos e históricos).\n\n"
            "- `is_paid=false` — retiro abierto, aún acumulando cobros.\n"
            "- `is_paid=true` — retiro cobrado (inmutable, histórico).\n\n"
            "**Filtro:** `?is_paid=true|false`"
        ),
        responses={200: _withdrawals_list_200, 401: r401_no_token},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=_TAG_WITHDRAWALS,
        operation_id="reward_withdrawals_retrieve",
        operation_summary="Detalle de un retiro (incluye imágenes cobradas)",
        responses={200: RewardWithdrawalDetailSerializer(), 401: r401_no_token, 404: r404_not_found},
    ),
)
class RewardWithdrawalViewSet(viewsets.ReadOnlyModelViewSet):
    """Retiros de recompensas del usuario autenticado."""

    http_method_names = ["get", "post"]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ["is_paid"]
    ordering_fields = ["created", "total_amount", "paid_at"]
    ordering = ["-created"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return RewardWithdrawal.objects.none()
        return (
            RewardWithdrawal.objects.filter(user=self.request.user)
            .annotate(images_count=Count("images"))
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RewardWithdrawalDetailSerializer
        return RewardWithdrawalSerializer

    @swagger_auto_schema(
        tags=_TAG_WITHDRAWALS,
        operation_id="reward_withdrawals_current",
        operation_summary="Retiro abierto actual",
        operation_description=(
            "Retorna el retiro abierto (`is_paid=false`) del usuario.\n\n"
            "Incluye el detalle de todas las imágenes cobradas acumuladas.\n\n"
            "Si no existe ningún retiro abierto, devuelve `null`."
        ),
        responses={
            200: RewardWithdrawalDetailSerializer(),
            401: r401_no_token,
        },
    )
    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """Retorna el retiro abierto actual del usuario con sus imágenes cobradas."""
        withdrawal = (
            RewardWithdrawal.objects.filter(user=request.user, is_paid=False)
            .annotate(images_count=Count("images"))
            .prefetch_related("images__reward_rule")
            .first()
        )
        if withdrawal is None:
            return Response(None)
        serializer = RewardWithdrawalDetailSerializer(withdrawal)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=_TAG_WITHDRAWALS,
        operation_id="reward_withdrawals_pay",
        operation_summary="Cobrar un retiro",
        operation_description=(
            "Marca el retiro como cobrado (`is_paid=true`).\n\n"
            "**Reglas:**\n"
            "- El retiro debe pertenecer al usuario autenticado.\n"
            "- El retiro debe estar abierto (`is_paid=false`).\n"
            "- Una vez cobrado, el retiro es inmutable (histórico).\n\n"
            "Después del cobro, los próximos cobros de imágenes crearán automáticamente un nuevo retiro abierto."
        ),
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT),
        responses={
            200: RewardWithdrawalSerializer(),
            400: r400_validation,
            401: r401_no_token,
            404: r404_not_found,
        },
    )
    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, pk=None):
        """Cobra el retiro: lo marca como pagado y lo congela como histórico."""
        withdrawal = self.get_object()

        if withdrawal.is_paid:
            raise ValidationError({"detail": "Este retiro ya fue cobrado anteriormente."})

        if withdrawal.total_amount <= 0:
            raise ValidationError({"detail": "No hay monto acumulado para cobrar."})

        withdrawal.pay()

        qs = RewardWithdrawal.objects.filter(pk=withdrawal.pk).annotate(
            images_count=Count("images")
        )
        serializer = RewardWithdrawalSerializer(qs.first())
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─── RewardBalanceView ────────────────────────────────────────────────────────


_balance_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "user": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        "total_amount": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Suma de todos los cobros (incluye retiros pagados y abiertos).",
        ),
        "total_rewards": openapi.Schema(type=openapi.TYPE_INTEGER),
        "open_withdrawal_amount": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Monto del retiro abierto actual (pendiente de cobrar).",
        ),
        "open_withdrawal_id": openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_UUID,
            x_nullable=True,
        ),
    },
)


class RewardBalanceView(APIView):
    """GET /api/rewards/balance/ — resumen global del usuario."""

    @swagger_auto_schema(
        tags=_TAG_BALANCE,
        operation_id="reward_balance",
        operation_summary="Saldo global de recompensas",
        operation_description=(
            "Devuelve el resumen global de recompensas del usuario autenticado:\n\n"
            "- `total_amount` — suma acumulada histórica de todos los cobros.\n"
            "- `open_withdrawal_amount` — monto del retiro abierto actual (pendiente).\n"
            "- `open_withdrawal_id` — UUID del retiro abierto para usar en `POST .../pay/`."
        ),
        responses={
            200: openapi.Response(description="**200 OK**", schema=_balance_schema),
            401: r401_no_token,
        },
    )
    def get(self, request):
        agg = Image.objects.filter(
            user=request.user,
            reward_claimed_at__isnull=False,
        ).aggregate(
            total_amount=Sum("reward_amount"),
            total_rewards=Count("id"),
        )
        open_w = RewardWithdrawal.objects.filter(user=request.user, is_paid=False).first()
        return Response({
            "user": request.user.pk,
            "total_amount": agg["total_amount"] or Decimal("0"),
            "total_rewards": agg["total_rewards"] or 0,
            "open_withdrawal_amount": open_w.total_amount if open_w else Decimal("0"),
            "open_withdrawal_id": open_w.pk if open_w else None,
        })
