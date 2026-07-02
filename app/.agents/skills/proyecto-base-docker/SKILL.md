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
| `Dockerfile` | Multi-stage at repo root: `dev` (compose) · `production` (Railway) |
| `docker-compose.yml` | Local dev: `web` (Django) + `web-db` (Postgres 16) |
| `app/requirements/` | `base.txt` (runtime) · `dev.txt` (+ linters) · `prod.txt` |
| `app/docker-entrypoint.sh` | Installed to `/usr/local/bin/` at build |
| `app/wait_for_db.py` | Installed to `/usr/local/bin/` at build |
| `.env.dev` | Local secrets (copy from `.env.dev-exemple`) |
| `railway.toml` | Railway: `Dockerfile` at repo root, healthcheck `/health` |

## Services (docker-compose)

| Service | Image / build | Host port | Notes |
|---|---|---|---|
| `web` | `context: .` **target `dev`** | 8000 | Healthcheck `GET /health` |
| `web-db` | `postgres:16-bookworm` | 5436→5432 | Named volume `pgdata`, network `proyecto-base` |

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
| Development | `POSTGRES_HOST` set (compose) | `dev` | `wait_for_db` → `migrate` → **gunicorn --reload** |
| Production | no `POSTGRES_HOST` (Railway) | `production` | `wait_for_db` → `collectstatic` → gunicorn |

**Railway migrations:** `preDeployCommand` in `railway.toml` runs `migrate` before deploy. On Railway (`RAILWAY_ENVIRONMENT` set), the entrypoint skips migrate at startup. For manual prod runs without Railway, migrate still runs in the entrypoint.

**Entrypoint passthrough:** If arguments are passed in production mode (e.g. Railway pre-deploy), the entrypoint runs them directly (`exec "$@"`).

**Collectstatic in dev:** skipped by default. Set `COLLECT_STATIC=1` to force it.

**Runtime user:** `appuser` (UID 1000).

## Volumes

| Volume | Mount | Why |
|---|---|---|
| `./app/apps`, `core`, `utils`, `manage.py` | bind (`docker-compose.dev.yml` only) | Hot reload |
| `staticfiles_data` → `/usr/src/app/staticfiles` | named | Avoid collectstatic conflicts |
| `pgdata` → `/var/lib/postgresql/data` | named | Persistent Postgres |

Runtime scripts live in `/usr/local/bin/` (safe with bind mounts).

### Windows

- Default: `docker compose up` (no bind mount).
- Hot reload: enable Docker Desktop **File sharing** for the repo drive, then use `docker-compose.dev.yml`.

## Healthcheck

- **HTTP:** `GET /health` → `{"status": "ok"}` (also `/health/`)
- **Compose / CI:** probe `/health`
- **Railway:** `healthcheckPath = "/health"` in `railway.toml`; Host header `healthcheck.railway.app` allowed in `prod.py`

## Railway production

**Build (Settings → Build):**

| Field | Value |
|---|---|
| Root Directory | *(empty)* |
| Dockerfile Path | `Dockerfile` |

**Required variables:**

```
PRODUCTION=1
SECRET_KEY=<secure-key>
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

Optional: `CORS_ALLOWED_ORIGINS=https://your-frontend.example` (auto-adds `RAILWAY_PUBLIC_DOMAIN`). Cloudinary vars. Do **not** set `POSTGRES_*` or `DATABASE` in Railway — use `DATABASE_URL` only.

**Pre-deploy:** `railway.toml` runs `migrate` via `preDeployCommand` before each deploy.

**Networking:** Generate Domain in Settings → Networking.

## When improving Docker here

1. Load `docker-patterns` skill for generic best practices.
2. Keep a single `Dockerfile` at repo root (`context: .`).
3. Pin base image digests on a schedule (`python:3.13-slim-bookworm@sha256:...`).
4. Use `security_opt: no-new-privileges` on `web` in compose.
5. Use `depends_on: condition: service_healthy` for `web-db`.
6. Never commit `.env.dev` — only `.env.dev-exemple`.
