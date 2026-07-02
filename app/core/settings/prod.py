import os

import dj_database_url

from ..logging import *  # noqa
from .base import *  # noqa

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = False

_RAILWAY_HOSTS = ("healthcheck.railway.app", "localhost", "127.0.0.1")

_allowed_hosts = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]
_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if _railway_domain:
    _allowed_hosts.append(_railway_domain)
_allowed_hosts.extend(_RAILWAY_HOSTS)
ALLOWED_HOSTS = _allowed_hosts or [".up.railway.app"]

CORS_ALLOW_ALL_ORIGINS = True

_csrf_origins = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
if _railway_domain:
    _csrf_origins.append(f"https://{_railway_domain}")
CSRF_TRUSTED_ORIGINS = _csrf_origins

# HTTPS settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ── Database ──────────────────────────────────────────────────────────────────
# Railway injects DATABASE_URL automatically when a Postgres service is linked.
# Set it in Railway service variables as: DATABASE_URL = ${{Postgres.DATABASE_URL}}
#
# Fallback: individual POSTGRES_* vars for other environments.
# Passwords with special characters are safe because Django's backend uses
# keyword args internally — no manual URL building here.
_database_url = os.environ.get("DATABASE_URL")

if _database_url:
    DATABASES = {
        "default": dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.environ.get("POSTGRES_HOST"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
            "USER": os.environ.get("POSTGRES_USER"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
            "NAME": os.environ.get("POSTGRES_DB_NAME"),
            "CONN_MAX_AGE": 60,
        }
    }

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}
