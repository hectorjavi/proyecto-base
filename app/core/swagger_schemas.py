"""
Reusable drf-yasg schemas and openapi.Response objects.

Import these in any viewset to keep error documentation consistent
across the entire API without repeating definitions.
"""

from drf_yasg import openapi

# ─── Raw error body schemas ───────────────────────────────────────────────────

validation_error_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    title="Error de validación",
    description=(
        "Diccionario donde cada clave es el nombre del campo con errores "
        "y el valor es una lista de mensajes. El campo especial "
        "`non_field_errors` contiene errores que no corresponden a un campo concreto."
    ),
    additional_properties=openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(type=openapi.TYPE_STRING),
    ),
    example={
        "username": ["Este campo es requerido."],
        "email": ["Ingrese un email válido."],
        "non_field_errors": ["Las contraseñas no coinciden."],
    },
)

unauthorized_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    title="No autenticado",
    description="Token ausente, expirado o con firma inválida.",
    properties={
        "detail": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="Las credenciales de autenticación no se proveyeron.",
        ),
        "code": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="not_authenticated",
        ),
        "messages": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "token_class": openapi.Schema(type=openapi.TYPE_STRING),
                    "token_type": openapi.Schema(type=openapi.TYPE_STRING),
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
    },
)

bad_credentials_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    title="Credenciales inválidas",
    description="El usuario no existe, la contraseña es incorrecta o la cuenta está inactiva.",
    properties={
        "detail": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="No active account found with the given credentials",
        ),
    },
)

token_invalid_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    title="Token inválido o expirado",
    properties={
        "detail": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="El token es inválido o ha expirado.",
        ),
        "code": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="token_not_valid",
        ),
    },
)

forbidden_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    title="Sin permisos",
    description="El usuario está autenticado pero no posee los permisos requeridos.",
    properties={
        "detail": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="No tiene permiso para realizar esta acción.",
        ),
    },
)

not_found_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    title="No encontrado",
    properties={
        "detail": openapi.Schema(
            type=openapi.TYPE_STRING,
            example="No encontrado.",
        ),
    },
)

# ─── Pre-built openapi.Response objects ───────────────────────────────────────

r400_validation = openapi.Response(
    description=(
        "**400 Bad Request** — Los datos enviados no pasaron la validación. "
        "El cuerpo contiene un objeto `{campo: [errores]}` con cada campo inválido."
    ),
    schema=validation_error_schema,
)

r401_no_token = openapi.Response(
    description=(
        "**401 Unauthorized** — No se proporcionó token de autenticación, "
        "el token ha expirado o la firma es inválida. "
        "Incluir header `Authorization: Bearer <access_token>`."
    ),
    schema=unauthorized_schema,
)

r401_bad_credentials = openapi.Response(
    description=(
        "**401 Unauthorized** — Credenciales incorrectas o cuenta inactiva. "
        "Verificar `username` y `password`."
    ),
    schema=bad_credentials_schema,
)

r401_token_invalid = openapi.Response(
    description=(
        "**401 Unauthorized** — El token JWT proporcionado no es válido o ha expirado. "
        "Obtener uno nuevo con `POST /api/auth/token/refresh/`."
    ),
    schema=token_invalid_schema,
)

r403_forbidden = openapi.Response(
    description=(
        "**403 Forbidden** — Autenticado pero sin los permisos necesarios "
        "para esta operación. Contactar al administrador para solicitar acceso."
    ),
    schema=forbidden_schema,
)

r404_not_found = openapi.Response(
    description="**404 Not Found** — El recurso solicitado no existe en la base de datos.",
    schema=not_found_schema,
)
