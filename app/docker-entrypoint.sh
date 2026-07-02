#!/bin/bash

set -e

# ── Wait for the database ─────────────────────────────────────────────────────
# Uses a Python script so the full DATABASE_URL (SSL, proxy, etc.) is respected.
# This works with Railway's managed Postgres, Heroku, and local docker-compose.
python /usr/local/bin/wait_for_db.py

# ── Apply migrations and start the server ────────────────────────────────────
_run_production() {
    echo "Running in Production Mode"
    python manage.py migrate --no-input --settings=core.settings.prod
    python manage.py collectstatic --no-input --settings=core.settings.prod
    # Default 1 worker; raise GUNICORN_WORKERS if the host has enough memory.
    GUNICORN_WORKERS="${GUNICORN_WORKERS:-1}"
    GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"
    exec gunicorn -w "${GUNICORN_WORKERS}" \
        --timeout "${GUNICORN_TIMEOUT}" \
        --env DJANGO_SETTINGS_MODULE=core.settings.prod \
        core.wsgi:application \
        --bind "0.0.0.0:${PORT:-8000}"
}

# Railway leaves startCommand empty — no CMD means $# is 0, so start gunicorn.
if [ "${PRODUCTION:-0}" -eq 1 ] || [ $# -eq 0 ]; then
    _run_production
else
    echo "Running in Developer Mode"
    python manage.py migrate --no-input --verbosity 0
    if [ "${COLLECT_STATIC:-0}" -eq 1 ]; then
        python manage.py collectstatic --no-input --clear
    fi
    exec "$@"
fi
