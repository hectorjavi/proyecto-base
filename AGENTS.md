# AGENTS.md — proyecto-base

Convenciones para agentes de IA que trabajan en este repositorio.

## Stack

- Python 3.13 · Django 5.2 LTS · DRF 3.16 · PostgreSQL 16
- Auth: JWT (simplejwt + blacklist)
- Local: Docker Compose · Prod: Railway

## django-safe-migration

- Django version: 5.2
- Deploy strategy: rolling deploy (Railway)
- Runtime guard: none
- Migration command: `docker compose exec web python manage.py sqlmigrate`
- Docs URL: none

## Docker (desarrollo local)

```bash
# Arranque estándar (Windows-safe — código en la imagen)
docker compose up -d --build

# Hot reload opcional
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

docker compose exec web python manage.py migrate
docker compose exec web python manage.py check
```

- Env file: `.env.dev` (plantilla: `.env.dev-exemple`) — secretos y Cloudinary
- Postgres en compose: `POSTGRES_*` definidos en `docker-compose.yml` (no en `.env.dev`)
- Detección dev/prod en entrypoint: `POSTGRES_HOST` → local · sin `POSTGRES_HOST` → Railway
- Railway: `preDeployCommand` migra antes del deploy; entrypoint omite migrate si `RAILWAY_ENVIRONMENT` está definido
- Imagen base Python pinneada por digest (re-pin periódico)
- Compose `web`: `security_opt: no-new-privileges`
- Collectstatic en dev: solo si `COLLECT_STATIC=1`
- Dev volumes: opcional en `docker-compose.dev.yml` (no se auto-carga)
- `wait_for_db.py` vive en `/usr/local/bin/` (no lo pisa el bind mount)
- Docker build: single `Dockerfile` at repo root — compose target `dev`, Railway target `production`
- Windows: si el bind mount falla, habilita file sharing en Docker Desktop para la unidad del repo

Ver skill `proyecto-base-docker` en `app/.agents/skills/` para detalle completo.

## Apps instaladas

- `apps.models.user` — modelo User custom + CRUD `/api/users/`
- `apps.auths` — JWT `/api/auth/`

## Skills del proyecto (`app/.agents/skills/`)

| Skill | Uso |
|---|---|
| `django-expert` | Modelos, DRF, tests, producción |
| `cdrf-expert` | ViewSets, MRO, hooks DRF |
| `django-safe-migration` | Migraciones PostgreSQL sin downtime |
| `docker-patterns` | Patrones genéricos Docker/Compose |
| `proyecto-base-docker` | Convenciones Docker de **este** repo |

## Calidad de código

Antes de commit:

```bash
docker compose exec web flake8 .
docker compose exec web black . --check
docker compose exec web isort . --check-only
```

CI: `.github/workflows/ci.yml` (flake8, black, isort, `manage.py check`, `check --deploy`, `manage.py test core`, build production + smoke `/health`).
