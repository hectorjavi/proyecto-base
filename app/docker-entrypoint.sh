#!/bin/bash

set -e

_should_run_production() {
    if [ "${PRODUCTION:-0}" -eq 1 ]; then
        return 0
    fi
    # Railway may pass startCommand="" as a single empty argument.
    if [ $# -eq 0 ]; then
        return 0
    fi
    if [ $# -eq 1 ] && [ -z "${1:-}" ]; then
        return 0
    fi
    return 1
}

if _should_run_production; then
    if [ -z "${SECRET_KEY:-}" ]; then
        echo "ERROR: SECRET_KEY is not set. Add it in Railway service variables." >&2
        exit 1
    fi
    if [ -z "${DATABASE_URL:-}" ]; then
        echo "ERROR: DATABASE_URL is not set. Link Postgres and set DATABASE_URL=\${{Postgres.DATABASE_URL}}." >&2
        exit 1
    fi
fi

echo "Starting container (PORT=${PORT:-8000}, PRODUCTION=${PRODUCTION:-0}, args=$#) ..." >&2

# ── Wait for the database ─────────────────────────────────────────────────────
python /usr/local/bin/wait_for_db.py

# ── Apply migrations and start the server ────────────────────────────────────
_run_production() {
    echo "Running in Production Mode"
    python manage.py migrate --no-input --settings=core.settings.prod
    python manage.py collectstatic --no-input --settings=core.settings.prod
    GUNICORN_WORKERS="${GUNICORN_WORKERS:-1}"
    GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"
    exec gunicorn -w "${GUNICORN_WORKERS}" \
        --timeout "${GUNICORN_TIMEOUT}" \
        --access-logfile - \
        --error-logfile - \
        --env DJANGO_SETTINGS_MODULE=core.settings.prod \
        core.wsgi:application \
        --bind "0.0.0.0:${PORT:-8000}"
}

if _should_run_production; then
    _run_production
else
    echo "Running in Developer Mode"
    python manage.py migrate --no-input --verbosity 0
    if [ "${COLLECT_STATIC:-0}" -eq 1 ]; then
        python manage.py collectstatic --no-input --clear
    fi
    exec "$@"
fi
