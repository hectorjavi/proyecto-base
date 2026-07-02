---
name: proyecto-base-docker
description: >-
  Docker and Docker Compose conventions for this Django proyecto-base repository.
  Use when editing Dockerfile, docker-compose.yml, docker-entrypoint.sh, Railway
  deployment, or running manage.py commands inside containers. Covers service names,
  env files, volume layout, and dev vs production startup behavior.
paths:
  - "Dockerfile*"
  - "**/docker-compose*.yml"
  - "**/docker-entrypoint.sh"
  - "railway.toml"
  - "AGENTS.md"
---

# Proyecto Base — Docker

## Layout

| Path | Purpose |
|---|---|
| `docker-compose.yml` | Local dev: `web` (Django) + `web-db` (Postgres 16) |
| `app/Dockerfile` | Multi-stage: `dev` (compose) · `production` (Railway, default) |
| `app/requirements/` | `base.txt` (runtime) · `dev.txt` (+ linters) · `prod.txt` |
| `app/docker-entrypoint.sh` | Copiado a `/usr/local/bin/` en build |
| `app/wait_for_db.py` | Copiado a `/usr/local/bin/` en build |
| `.env.dev` | Local secrets (copy from `.env.dev-exemple`) |
| `railway.toml` | Production build from `app/Dockerfile` |

## Services (docker-compose)

| Service | Image / build | Host port | Notes |
|---|---|---|---|
| `web` | `build: ./app` **target `dev`** | 8000 | Healthcheck `GET /health/` |
| `web-db` | `postgres:16-bookworm` | 5436→5432 | Named volume `pgdata`, locales UTF-8 |

**Important:** `.env.dev` must use `POSTGRES_HOST=web-db` (Docker DNS service name).

## Standard commands

```bash
# Start stack (default — code baked in image)
docker compose up -d --build

# Hot reload (optional)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# Django management
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py check

# Migrations SQL (django-safe-migration)
docker compose exec web python manage.py sqlmigrate <app> <migration>

# Linters
docker compose exec web flake8 .
docker compose exec web black . --check
docker compose exec web isort . --check-only

# Logs / reset DB
docker compose logs -f web
docker compose down -v && docker compose up -d --build
```

## Dev vs production entrypoint

| Mode | Trigger | Image target | Behavior |
|---|---|---|---|
| Development | `PRODUCTION=0` | `dev` | `wait_for_db` → `migrate` → **gunicorn --reload** |
| Production | `PRODUCTION=1` | `production` | `wait_for_db` → `migrate` → `collectstatic` → gunicorn |

**Collectstatic in dev:** skipped by default. Set `COLLECT_STATIC=1` to force it on startup.

**Runtime user:** `appuser` (UID 1000) — no `chmod 777`.

## Volumes

| Volume | Mount | Why |
|---|---|---|
| `./app/apps`, `core`, `utils`, `manage.py` | bind (`docker-compose.dev.yml` only) | Hot reload sin pisar scripts de runtime |
| `staticfiles_data` → `/usr/src/app/staticfiles` | named | Evita conflictos con collectstatic |
| `pgdata` → `/var/lib/postgresql/data` | named | Postgres persistente |

**Runtime fuera del bind mount:** `docker-entrypoint.sh` y `wait_for_db.py` están en `/usr/local/bin/`.

### Windows

- **Por defecto** usa `docker compose up` (sin `docker-compose.dev.yml`).
- Si necesitas hot reload: Docker Desktop → **File sharing** para la unidad del repo, luego el comando con `-f docker-compose.dev.yml`.

## Healthcheck

- **HTTP:** `GET /health/` → `{"status": "ok"}` (sin auth)
- **Compose:** probe en `docker-compose.yml` cada 30s
- **Production image:** `HEALTHCHECK` en Dockerfile target `production`
- **CI:** GitHub Actions valida el endpoint tras levantar `web`

## Expected logs (not errors)

| Message | Meaning | Action |
|---|---|---|
| Postgres: `Skipping initialization` | Volume `pgdata` already has data | Normal on restarts; use `docker compose down -v` only to reset DB |
| Postgres: `checkpoint complete` | Routine WAL maintenance | Hidden with `log_min_messages=warning` in compose |
| Django: `development server` WARNING | Only if using `runserver` | Dev stack uses **gunicorn --reload** instead |
| `No migrations to apply` | DB is up to date | Normal |

Set `WAIT_DB_VERBOSE=1` in `.env.dev` to see every DB retry during startup.

## Railway production

- Set `PRODUCTION=1`, `SECRET_KEY`, Cloudinary vars, and `DATABASE_URL` (linked Postgres).
- `railway.toml` builds `app/Dockerfile` **target `production`**; entrypoint handles migrate + gunicorn.
- Do **not** use docker-compose in Railway; compose is local dev only.

## When improving Docker here

1. Load `docker-patterns` skill for generic best practices.
2. Keep build context as `./app` (not repo root).
3. Prefer `depends_on: condition: service_healthy` for `web-db`.
4. Never commit `.env.dev` — only `.env.dev-exemple`.
