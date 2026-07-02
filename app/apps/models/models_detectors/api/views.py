from django.http import FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.swagger_schemas import r401_no_token

from .. import services

_TAG = ["Detectores"]

_onnx_200 = openapi.Response(
    description=(
        "**200 OK** — Cuerpo binario del modelo ONNX "
        "`retinanet_bird_lite.onnx` (descarga / streaming). "
        "Si el archivo no existe localmente, se descarga antes desde Google Drive "
        "(la primera petición puede tardar varios minutos)."
    ),
    schema=openapi.Schema(type=openapi.TYPE_STRING, format="binary"),
)

_model_download_failed_503 = openapi.Response(
    description=(
        "**503 Service Unavailable** — No se pudo descargar el modelo "
        "desde el almacenamiento externo (red, Drive o cuota)."
    ),
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "detail": openapi.Schema(type=openapi.TYPE_STRING),
            "code": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
)


class RetinaNetBirdLiteModelView(APIView):
    """Sirve el ONNX RetinaNet bird lite; lo obtiene de Drive si no está en disco."""

    @swagger_auto_schema(
        tags=_TAG,
        operation_id="detectors_retinanet_bird_lite_model",
        operation_summary="Descargar modelo RetinaNet bird lite (ONNX)",
        operation_description=(
            "Devuelve `retinanet_bird_lite.onnx`.\n\n"
            "- Si ya existe en `apps.models.models_detectors.models/`, se sirve desde disco.\n"
            "- Si no existe, se descarga automáticamente desde Google Drive (gdown); "
            "el primer acceso puede ser lento (~150 MB).\n\n"
            "Requiere JWT (igual que el resto de la API)."
        ),
        responses={
            200: _onnx_200,
            401: r401_no_token,
            503: _model_download_failed_503,
        },
    )
    def get(self, request):
        try:
            path = services.ensure_retinanet_bird_lite()
        except Exception:
            return Response(
                {
                    "detail": (
                        "No se pudo obtener el modelo. "
                        "Comprueba la red o los permisos del enlace en Google Drive."
                    ),
                    "code": "model_download_failed",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        handle = path.open("rb")
        return FileResponse(
            handle,
            as_attachment=True,
            filename=path.name,
            content_type="application/octet-stream",
        )
