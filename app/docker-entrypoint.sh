#!/bin/bash

set -e

# Local compose sets POSTGRES_HOST; Railway uses DATABASE_URL only.
production_mode() {
    [ -z "${POSTGRES_HOST:-}" ]
}

if production_mode; then
    : "${SECRET_KEY:?ERROR: SECRET_KEY is not set.}"
    : "${DATABASE_URL:?ERROR: DATABASE_URL is not set. Link Postgres in Railway.}"
fi

python /usr/local/bin/wait_for_db.py

if production_mode; then
    echo "Running in Production Mode"
    python manage.py migrate --no-input --settings=core.settings.prod
    python manage.py collectstatic --no-input --settings=core.settings.prod
    exec gunicorn -w "${GUNICORN_WORKERS:-1}" \
        --timeout "${GUNICORN_TIMEOUT:-120}" \
        --access-logfile - \
        --error-logfile - \
        --env DJANGO_SETTINGS_MODULE=core.settings.prod \
        core.wsgi:application \
        --bind "0.0.0.0:${PORT:-8000}"
fi

echo "Running in Developer Mode"
python manage.py migrate --no-input --verbosity 0
if [ "${COLLECT_STATIC:-0}" -eq 1 ]; then
    python manage.py collectstatic --no-input --clear
fi
exec "$@"
