import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "SECRET_KEY environment variable is required. Copy .env.dev-exemple to .env.dev."
    )

DEBUG = True

ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

# Database
POSTGRES_DB = {
    "ENGINE": "django.db.backends.postgresql",
    "HOST": os.environ.get("POSTGRES_HOST"),
    "PORT": os.environ.get("POSTGRES_PORT"),
    "USER": os.environ.get("POSTGRES_USER"),
    "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
    "NAME": os.environ.get("POSTGRES_DB_NAME"),
}

DATABASES = {"default": POSTGRES_DB}

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405

# File storage (Django 4.2+ STORAGES dict replaces deprecated
# DEFAULT_FILE_STORAGE and STATICFILES_STORAGE settings)
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Cloudinary configuration
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

DBBACKUP_FILENAME_TEMPLATE = "{datetime}.sql"
DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": BASE_DIR / "backup"}  # noqa
