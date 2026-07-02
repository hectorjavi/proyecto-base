"""
Django settings for core project.

Targeting Django 5.2 LTS (Python 3.13).

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# Application definition

BASE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

LOCAL_APPS = [
    "apps.models.user",
    "apps.models.image",
    "apps.models.tag",
    "apps.models.image_tag",
    "apps.models.reward",
    "apps.models.models_detectors",
]

THIRD_APPS = [
    "dbbackup",
    "cloudinary",
    "cloudinary_storage",
    "corsheaders",
    "rest_framework",
    "drf_yasg",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS


BASE_MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

LOCAL_MIDDLEWARE = []

THIRD_MIDDLEWARE = []

MIDDLEWARE = BASE_MIDDLEWARE + LOCAL_MIDDLEWARE + THIRD_MIDDLEWARE


ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # IsAuthenticated: any valid JWT grants access; per-view permission_classes
    # handle fine-grained ACL (e.g. HasUserPermissionUser on the user viewset).
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "EXCEPTION_HANDLER": "utils.api.exception_handlers.custom_exception_handler",
}

AUTH_USER_MODEL = "user.User"


WSGI_APPLICATION = "core.wsgi.application"


# DBBACKUP_FILENAME_TEMPLATE = '{datetime}.sql'
# DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
# DBBACKUP_STORAGE_OPTIONS = {'location': BASE_DIR / 'backup'}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "es-es"

TIME_ZONE = "America/Lima"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"

MEDIA_URL = "/media/"  # or any prefix you choose

MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Swagger / drf-yasg ────────────────────────────────────────────────────────
SWAGGER_SETTINGS = {
    # JWT Bearer token — sends: Authorization: Bearer <token>
    # Users must type the full value including the "Bearer " prefix.
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": (
                "Autenticación JWT. "
                "Obtén tu token en POST /api/auth/token/ "
                "e ingrésalo aquí como: Bearer <access_token>"
            ),
        }
    },
    # No Django session login form in Swagger (JWT only)
    "USE_SESSION_AUTH": False,
    # Inline JSON editor for request bodies
    "JSON_EDITOR": True,
    # HTTP methods that show a "Try it out" button
    "SUPPORTED_SUBMIT_METHODS": ["get", "post", "put", "patch", "delete"],
    # Keep the token across page reloads (stored in localStorage)
    "PERSIST_AUTH": True,
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "REFETCH_SCHEMA_ON_LOGOUT": True,
    # UX
    "DEEP_LINKING": True,
    "SHOW_EXTENSIONS": True,
    "SHOW_COMMON_EXTENSIONS": True,
    "DEFAULT_MODEL_RENDERING": "example",
    "DEFAULT_MODEL_DEPTH": 3,
    "OPERATIONS_SORTER": "alpha",
    "TAGS_SORTER": "alpha",
    "DOC_EXPANSION": "list",
    "DISPLAY_OPERATION_ID": False,
}

# ── SimpleJWT ─────────────────────────────────────────────────────────────────
from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}
