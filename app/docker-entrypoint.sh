#!/bin/bash

set -e

# ── Wait for the database ─────────────────────────────────────────────────────
# Uses a Python script so the full DATABASE_URL (SSL, proxy, etc.) is respected.
# This works with Railway's managed Postgres, Heroku, and local docker-compose.
python /usr/src/app/wait_for_db.py

# ── Apply migrations and start the server ────────────────────────────────────
if [ "${PRODUCTION:-0}" -eq 1 ]; then
    echo "Running in Production Mode"
    python manage.py migrate --no-input --settings=core.settings.prod
    python manage.py collectstatic --no-input --settings=core.settings.prod
    # Default 1 worker: each process loads the full CNN (~hundreds of MB RAM).
    # Raise GUNICORN_WORKERS only if the host has enough memory for N × model.
    GUNICORN_WORKERS="${GUNICORN_WORKERS:-1}"
    GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"
    exec gunicorn -w "${GUNICORN_WORKERS}" \
        --timeout "${GUNICORN_TIMEOUT}" \
        --env DJANGO_SETTINGS_MODULE=core.settings.prod \
        core.wsgi:application \
        --bind "0.0.0.0:${PORT:-8000}"
else
    echo "Running in Developer Mode"
    python manage.py migrate --no-input
    python manage.py collectstatic --no-input --clear
    exec "$@"
fi
