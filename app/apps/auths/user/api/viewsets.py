from django.contrib.auth.hashers import make_password
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.models.user.api.serializers import UserSerializer
from core.swagger_schemas import (
    r400_validation,
    r401_bad_credentials,
    r401_no_token,
    r401_token_invalid,
)

from . import serializers

_TAG = ["Autenticación"]

# ─── Request / response schemas specific to auth ──────────────────────────────

_login_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["username", "password"],
    properties={
        "username": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Nombre de usuario",
            example="admin",
        ),
        "password": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Contraseña del usuario",
            example="mypassword123",
        ),
    },
)

_login_response_200 = openapi.Response(
    description=(
        "**200 OK** — Login exitoso. "
        "Guarda el `access` token y úsalo en el header `Authorization: Bearer <token>`."
    ),
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "access": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Token de acceso JWT (válido 60 min)",
                example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.abc",
            ),
            "refresh": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Token de refresco JWT (válido 7 días)",
                example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxfQ.xyz",
            ),
            "user": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Datos básicos del usuario autenticado.",
            ),
        },
    ),
)

_refresh_response_200 = openapi.Response(
    description="**200 OK** — Nuevo access token generado.",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "access": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Nuevo access token",
                example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new.token",
            ),
            "refresh": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Nuevo refresh token (emitido cuando ROTATE_REFRESH_TOKENS=True)",
                example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new.refresh",
            ),
        },
    ),
)

_refresh_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["refresh"],
    properties={
        "refresh": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Refresh token vigente.",
            example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh.token",
        )
    },
)

_verify_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["token"],
    properties={
        "token": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Token JWT a validar.",
            example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.access.token",
        )
    },
)

_blacklist_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["refresh"],
    properties={
        "refresh": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Refresh token que se agregará a blacklist.",
            example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.refresh.token",
        )
    },
)

_change_password_400 = openapi.Response(
    description=(
        "**400 Bad Request** — Posibles causas:\n"
        "- `current_password` no coincide con la contraseña actual\n"
        "- `new_password` es igual a `current_password`\n"
        "- Algún campo requerido está ausente"
    ),
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "current_password": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                example=["Contraseña incorrecta."],
            ),
            "new_password": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                example=["Ingrese una contraseña diferente a la anterior."],
            ),
        },
    ),
)

_empty_200 = openapi.Response(
    description="**200 OK** — Operación completada exitosamente.",
    schema=openapi.Schema(type=openapi.TYPE_OBJECT),
)


# ─── Login ────────────────────────────────────────────────────────────────────


class LoginView(TokenObtainPairView):
    """Obtiene un par de tokens JWT (access + refresh) a cambio de credenciales."""

    serializers_class = TokenObtainPairSerializer

    @swagger_auto_schema(
        operation_id="auth_token_obtain",
        operation_summary="Login — obtener tokens",
        operation_description=(
            "Autentica al usuario con `username` y `password`.\n\n"
            "En caso de éxito devuelve:\n"
            "- **access** token (válido 60 min) → úsalo en `Authorization: Bearer <token>`\n"
            "- **refresh** token (válido 7 días) → guárdalo para renovar el access\n"
            "- **user** con los datos básicos del usuario"
        ),
        request_body=_login_request,
        responses={
            200: _login_response_200,
            400: r400_validation,
            401: r401_bad_credentials,
        },
        tags=_TAG,
    )
    def post(self, request, *args, **kwargs):
        login_serializer = self.serializers_class(data=request.data)
        login_serializer.is_valid(raise_exception=True)

        user = UserSerializer(
            login_serializer.user,
            context={"request": request},
        ).data

        response = login_serializer.validated_data
        response["user"] = user
        return Response(response, status=status.HTTP_200_OK)


# ─── Documented wrappers for simplejwt built-in views ─────────────────────────


class TokenRefreshViewDoc(TokenRefreshView):
    """Renueva el access token usando un refresh token válido."""

    @swagger_auto_schema(
        operation_id="auth_token_refresh",
        operation_summary="Renovar access token",
        operation_description=(
            "Intercambia un **refresh token** válido por un nuevo **access token**.\n\n"
            "Con `ROTATE_REFRESH_TOKENS=True` también se emite "
            "un nuevo refresh token y el anterior queda en la blacklist automáticamente."
        ),
        request_body=_refresh_request,
        responses={
            200: _refresh_response_200,
            401: r401_token_invalid,
        },
        tags=_TAG,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenVerifyViewDoc(TokenVerifyView):
    """Verifica si un token JWT es válido y no ha expirado."""

    @swagger_auto_schema(
        operation_id="auth_token_verify",
        operation_summary="Verificar token",
        operation_description=(
            "Comprueba que el token es sintácticamente correcto, no ha sido "
            "manipulado y no ha expirado.\n\n"
            "Devuelve `200 {}` si el token es válido, o `401` si no lo es.\n\n"
            "Útil para validar el token desde el frontend antes de hacer una petición."
        ),
        request_body=_verify_request,
        responses={
            200: _empty_200,
            401: r401_token_invalid,
        },
        tags=_TAG,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenBlacklistViewDoc(TokenBlacklistView):
    """Invalida un refresh token (logout seguro)."""

    @swagger_auto_schema(
        operation_id="auth_token_blacklist",
        operation_summary="Logout — invalidar refresh token",
        operation_description=(
            "Agrega el **refresh token** a la blacklist, impidiendo que pueda "
            "usarse para obtener nuevos access tokens.\n\n"
            "⚠️ El **access token** sigue siendo válido hasta que expire. "
            "Para un logout inmediato también se debe descartar el access token "
            "en el cliente."
        ),
        request_body=_blacklist_request,
        responses={
            200: _empty_200,
            400: r400_validation,
            401: r401_token_invalid,
        },
        tags=_TAG,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# ─── Authenticated user profile ───────────────────────────────────────────────


class UserMeView(APIView):
    """Perfil del usuario autenticado actualmente."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="auth_me_retrieve",
        operation_summary="Mi perfil",
        operation_description="Devuelve los datos completos del usuario actualmente autenticado.",
        responses={
            200: UserSerializer(),
            401: r401_no_token,
        },
        tags=_TAG,
    )
    def get(self, request):
        serializer_data = UserSerializer(request.user, context={"request": request})
        return Response(serializer_data.data)

    @swagger_auto_schema(
        operation_id="auth_me_update",
        operation_summary="Actualizar mi perfil",
        operation_description=(
            "Actualiza parcialmente los datos del usuario autenticado.\n\n"
            "Solo se modifican los campos que se envíen en el cuerpo. "
            "El `id` nunca cambia."
        ),
        request_body=serializers.UserMeUpdateSerializer(),
        responses={
            200: UserSerializer(),
            400: r400_validation,
            401: r401_no_token,
        },
        tags=_TAG,
    )
    def patch(self, request):
        user = request.user
        serializer_data = serializers.UserMeUpdateSerializer(
            user,
            data=request.data,
            partial=True,
        )
        serializer_data.is_valid(raise_exception=True)
        serializer_data.save()

        serializer_data_new = UserSerializer(
            user,
            context={"request": request},
        )
        return Response(serializer_data_new.data, status=status.HTTP_200_OK)


class UserMePassView(APIView):
    """Cambio de contraseña del usuario autenticado."""

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id="auth_me_change_password",
        operation_summary="Cambiar contraseña",
        operation_description=(
            "Cambia la contraseña del usuario autenticado.\n\n"
            "**Reglas:**\n"
            "- Se requiere `current_password` correcta para confirmar la identidad\n"
            "- `new_password` debe ser diferente a `current_password`\n\n"
            "Después de cambiar la contraseña se recomienda hacer logout "
            "y volver a iniciar sesión con la nueva contraseña."
        ),
        request_body=serializers.UserMeUpdatePssSerializer(),
        responses={
            200: _empty_200,
            400: _change_password_400,
            401: r401_no_token,
        },
        tags=_TAG,
    )
    def post(self, request):
        serializer_data = serializers.UserMeUpdatePssSerializer(data=request.data)
        serializer_data.is_valid(raise_exception=True)

        user = request.user
        current_password = serializer_data.validated_data["current_password"]
        new_password = serializer_data.validated_data["new_password"]

        if not user.check_password(current_password):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"current_password": ["Contraseña incorrecta."]},
            )

        user.password = make_password(new_password)
        user.save(update_fields=["password"])

        return Response({}, status=status.HTTP_200_OK)
