from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

_DESCRIPTION = """
# Backend REST API

API RESTful construida con **Django 5.2 LTS** · **Django REST Framework 3.16** · **JWT Authentication**.

---

## Autenticación JWT

Todos los endpoints (excepto login y refresh) requieren un **Bearer token** válido.

### Paso 1 — Obtener tokens

`POST /api/auth/token/` con tus credenciales:

```json
{ "username": "tu_usuario", "password": "tu_contraseña" }
```

Respuesta exitosa:

```json
{
  "access":  "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": { "id": "...", "username": "...", "email": "..." }
}
```

| Campo | Validez | Uso |
|---|---|---|
| `access` | 60 minutos | Enviarlo en cada petición como `Bearer <token>` |
| `refresh` | 7 días | Renovar el `access` sin volver a hacer login |

### Paso 2 — Autorizar en Swagger

Haz clic en **Authorize** (arriba a la derecha) e ingresa:

```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Incluir el prefijo `Bearer ` seguido de un espacio antes del token.

### Paso 3 — Renovar token expirado

`POST /api/auth/token/refresh/` con el `refresh` token para obtener un nuevo `access` sin re-autenticarse.

### Paso 4 — Logout

`POST /api/auth/token/blacklist/` con el `refresh` token lo invalida en la blacklist.

---

## Códigos de error

Todos los errores siguen la convención de DRF y tienen la siguiente estructura:

### 400 Bad Request — Error de validación

Se produce cuando los datos enviados no pasan las reglas de validación.
El cuerpo contiene un objeto donde cada clave es el campo con errores:

```json
{
  "username": ["Este campo es requerido."],
  "email":    ["Ingrese un email válido."],
  "non_field_errors": ["Las contraseñas no coinciden."]
}
```

### 401 Unauthorized — Sin autenticación o token inválido

```json
{
  "detail": "Las credenciales de autenticación no se proveyeron.",
  "code":   "not_authenticated"
}
```

Causas comunes:
- Header `Authorization` ausente
- Token expirado (renovar con `POST /api/auth/token/refresh/`)
- Token manipulado o con firma inválida
- Credenciales de login incorrectas

### 403 Forbidden — Sin permisos

```json
{ "detail": "No tiene permiso para realizar esta acción." }
```

El usuario está autenticado pero no posee el permiso de modelo requerido
(`add_*`, `view_*`, `change_*`, `delete_*`). Contactar al administrador.

### 404 Not Found — Recurso inexistente

```json
{ "detail": "No encontrado." }
```

El `id` proporcionado no corresponde a ningún registro en la base de datos.

### 500 Internal Server Error

Error inesperado en el servidor. Revisar los logs del contenedor `web`.

---

## Referencia rápida de endpoints

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| POST | `/api/auth/token/` | No | Login — obtener access y refresh token |
| POST | `/api/auth/token/refresh/` | No | Renovar access token |
| POST | `/api/auth/token/verify/` | No | Verificar validez de un token |
| POST | `/api/auth/token/blacklist/` | Sí | Logout — invalidar refresh token |
| GET | `/api/auth/me/` | Sí | Obtener perfil del usuario autenticado |
| PATCH | `/api/auth/me/` | Sí | Actualizar perfil propio |
| POST | `/api/auth/me/reset_password/` | Sí | Cambiar contraseña |
| GET | `/api/images/` | Sí | Listar imágenes propias (paginado) |
| POST | `/api/images/` | Sí | Subir imagen (multipart/form-data) |
| POST | `/api/images/upload-base64/` | Sí | Subir imagen en base64 |
| GET | `/api/images/{id}/` | Sí | Obtener detalle de una imagen |
| PUT | `/api/images/{id}/` | Sí | Actualizar imagen (completo) |
| PATCH | `/api/images/{id}/` | Sí | Actualizar imagen (parcial) |
| DELETE | `/api/images/{id}/` | Sí | Eliminar imagen y archivo en storage |
| GET | `/api/tags/` | Sí | Listar etiquetas en árbol (solo raíces) |
| GET | `/api/tags/{id}/` | Sí | Obtener una etiqueta con su subárbol |

---

## Stack técnico

| Componente | Versión |
|---|---|
| Python | 3.13 |
| Django | 5.2 LTS |
| Django REST Framework | 3.16 |
| djangorestframework-simplejwt | 5.5 |
| PostgreSQL | 16 |
| drf-yasg | 1.21 |
| Cloudinary | 1.44 |
"""

schema_view = get_schema_view(
    openapi.Info(
        title="Backend API",
        default_version="v1",
        description=_DESCRIPTION,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(
            name="Soporte Técnico",
            email="hectorjavier@upeu.edu.pe",
        ),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
