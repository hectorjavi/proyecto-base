# Proyecto Base — Django + PostgreSQL + Docker

API REST construida con Django 5.2 LTS, PostgreSQL y Docker. Incluye autenticación JWT, CRUD de usuarios, documentación Swagger, almacenamiento en Cloudinary y despliegue en Railway.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.13 |
| Backend | Django 5.2 LTS, Django REST Framework 3.16 |
| Base de datos | PostgreSQL 16 (psycopg2) |
| Autenticación | JWT (djangorestframework-simplejwt + blacklist) |
| Documentación | drf-yasg (Swagger / ReDoc) |
| Almacenamiento | Cloudinary (django-cloudinary-storage) |
| Archivos estáticos | WhiteNoise |
| Contenerización | Docker + Docker Compose |
| Despliegue | Railway |

---

## Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/install/) instalados.

---

## Variables de entorno

El proyecto separa configuración por entorno. **Nunca commitees** `.env.dev` (solo la plantilla `.env.dev-exemple`).

### Resumen

| Entorno | Dónde se definen | Settings Django | Cómo arranca |
|---|---|---|---|
| **Desarrollo** | `.env.dev` + `docker-compose.yml` | `core.settings.local` | `POSTGRES_HOST=web-db` → modo dev |
| **Producción (Railway)** | Variables del servicio en Railway | `core.settings.prod` | Sin `POSTGRES_HOST`, solo `DATABASE_URL` |

El entrypoint detecta el modo así: si existe `POSTGRES_HOST` → desarrollo; si no → producción.

---

### Desarrollo local

#### 1. Crear `.env.dev`

```bash
cp .env.dev-exemple .env.dev
```

#### 2. Variables en `.env.dev` (tu máquina)

| Variable | ¿Obligatoria? | Descripción | Ejemplo |
|---|---|---|---|
| `SECRET_KEY` | **Sí** | Clave Django (mín. ~50 caracteres recomendado) | `django-insecure-dev-...` o generada |
| `CLOUDINARY_CLOUD_NAME` | Sí* | Cuenta Cloudinary | `your-cloud-name` |
| `CLOUDINARY_API_KEY` | Sí* | API key Cloudinary | `your-api-key` |
| `CLOUDINARY_API_SECRET` | Sí* | API secret Cloudinary | `your-api-secret` |
| `PRODUCTION` | No | Convención documental (`0` en dev) | `0` |

\* Obligatorias si usas subida de archivos/media. Sin credenciales válidas, las operaciones con media pueden fallar.

**Plantilla mínima (`.env.dev`):**

```env
# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Django
PRODUCTION=0
SECRET_KEY=cambia-esto-por-una-clave-larga-y-aleatoria-de-al-menos-50-chars
```

Generar `SECRET_KEY`:

```bash
docker compose run --rm --no-deps --entrypoint python web -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 3. Variables en `docker-compose.yml` (no duplicar en `.env.dev`)

Compose inyecta Postgres y flags de entorno al servicio `web`:

| Variable | Valor por defecto | Uso |
|---|---|---|
| `POSTGRES_HOST` | `web-db` | Host del contenedor Postgres |
| `POSTGRES_PORT` | `5432` | Puerto interno |
| `POSTGRES_USER` | `postgres` | Usuario BD |
| `POSTGRES_PASSWORD` | `postgres` | Contraseña BD |
| `POSTGRES_DB_NAME` | `web_db` | Nombre de la base |
| `PRODUCTION` | `0` | Marcador de entorno dev |
| `DJANGO_SETTINGS_MODULE` | `core.settings.local` | Settings (vía comando gunicorn) |

Postgres del servicio `web-db` usa `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (mismos valores).

**No definas `DATABASE_URL` en desarrollo local** — el entrypoint y `local.py` usan `POSTGRES_*`.

#### 4. Variables opcionales (desarrollo)

| Variable | Default | Descripción |
|---|---|---|
| `COLLECT_STATIC` | `0` | `1` fuerza `collectstatic` en cada arranque |
| `WAIT_DB_VERBOSE` | `0` | `1` muestra reintentos de conexión a BD |
| `WAIT_DB_MAX_RETRIES` | `60` | Reintentos máximos antes de fallar |
| `CREATE_DEFAULT_SUPERUSER` | — | `1` crea usuario `test@gmail.com` aunque `DEBUG=False` |

#### 5. No usar en desarrollo local

| Variable | Motivo |
|---|---|
| `DATABASE_URL` | Reservada para Railway/producción |
| `POSTGRES_*` en `.env.dev` | Ya están en `docker-compose.yml`; duplicar genera confusión |
| `ALLOWED_HOSTS`, `CORS_*` | En dev: `ALLOWED_HOSTS=*`, CORS abierto en `local.py` |

---

### Producción (Railway)

Settings: `core.settings.prod` · Imagen Docker: target `production`.

#### Variables obligatorias

| Variable | Valor en Railway | Descripción |
|---|---|---|
| `SECRET_KEY` | Clave larga y aleatoria | Sin esto Django no arranca |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | URL al vincular el servicio Postgres |

`DATABASE_URL` la inyecta Railway al enlazar Postgres. Configúrala en **Variables** del servicio web:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

#### Variables recomendadas (Cloudinary)

| Variable | Descripción |
|---|---|
| `CLOUDINARY_CLOUD_NAME` | Mismo que en dev, con credenciales de prod |
| `CLOUDINARY_API_KEY` | API key de producción |
| `CLOUDINARY_API_SECRET` | API secret de producción |

#### Variables opcionales (producción)

| Variable | Descripción | Ejemplo |
|---|---|---|
| `PRODUCTION` | Convención (`1` en prod) | `1` |
| `ALLOWED_HOSTS` | Hosts extra (coma-separados) | `mi-dominio.com,api.mi-dominio.com` |
| `CORS_ALLOWED_ORIGINS` | Orígenes frontend permitidos | `https://app.ejemplo.com` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes CSRF (si aplica) | `https://app.ejemplo.com` |
| `GUNICORN_WORKERS` | Workers gunicorn | `2` |
| `GUNICORN_TIMEOUT` | Timeout en segundos | `120` |

Railway suele inyectar automáticamente:

| Variable | Uso en el proyecto |
|---|---|
| `RAILWAY_PUBLIC_DOMAIN` | Se añade a `ALLOWED_HOSTS`, CORS y CSRF |
| `RAILWAY_ENVIRONMENT` | Omite `migrate` en arranque (lo hace `preDeployCommand`) |
| `PORT` | Puerto donde escucha gunicorn |

`healthcheck.railway.app` y `.up.railway.app` ya están contemplados en `prod.py`.

#### No usar en Railway

| Variable | Motivo |
|---|---|
| `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB_NAME` | Usa solo `DATABASE_URL` |
| `DATABASE` | Legacy; no se usa en este proyecto |
| Bind mounts / `.env.dev` | Railway usa variables del dashboard, no archivos locales |

#### Ejemplo — panel Railway (servicio web)

```
SECRET_KEY=<genera-una-clave-segura>
DATABASE_URL=${{Postgres.DATABASE_URL}}
PRODUCTION=1

CLOUDINARY_CLOUD_NAME=<tu-cloud>
CLOUDINARY_API_KEY=<tu-key>
CLOUDINARY_API_SECRET=<tu-secret>

# Solo si tienes frontend en otro dominio:
CORS_ALLOWED_ORIGINS=https://tu-frontend.ejemplo.com
```

---

## Instalación y puesta en marcha (desarrollo)

### 1. Configurar variables de entorno

```bash
cp .env.dev-exemple .env.dev
```

Edita `.env.dev` con tu `SECRET_KEY` y credenciales Cloudinary. Los detalles están en [Variables de entorno → Desarrollo local](#desarrollo-local).

### 2. Construir y levantar los contenedores

```bash
docker-compose up -d --build
```

Tras cambios de código, reconstruye la imagen (`docker compose up -d --build`) o usa hot reload:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

### 3. Acceder a la aplicación

| Recurso | URL |
|---|---|
| API Docs (Swagger) | http://localhost:8000/docs/ |
| API Docs (ReDoc) | http://localhost:8000/redocs/ |
| Django Admin | http://localhost:8000/admin/ |
| PostgreSQL (externo) | `localhost:5436` |

### 4. Usuario de prueba (solo desarrollo)

Con `DEBUG=True` (settings local), tras la primera migración se crea un superusuario de conveniencia:

```
Email:    test@gmail.com
Usuario:  test
Password: test
```

En producción **no** se crea. Para forzarlo en otro entorno: `CREATE_DEFAULT_SUPERUSER=1` (solo dev/staging).

---

## API — Endpoints disponibles

Todos los endpoints (excepto login y refresh) requieren header `Authorization: Bearer <access_token>`.

### Autenticación (`/api/auth/`)

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/health` | No | Liveness probe (also `/health/`) |
| POST | `/api/auth/token/` | No | Login — obtener access y refresh token |
| POST | `/api/auth/token/refresh/` | No | Renovar access token |
| POST | `/api/auth/token/verify/` | No | Verificar validez de un token |
| POST | `/api/auth/token/blacklist/` | Sí | Logout — invalidar refresh token |
| GET | `/api/auth/me/` | Sí | Obtener perfil del usuario autenticado |
| PATCH | `/api/auth/me/` | Sí | Actualizar perfil propio |
| POST | `/api/auth/me/reset_password/` | Sí | Cambiar contraseña |

### Usuarios (`/api/users/`)

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/api/users/` | Sí | Listar usuarios (paginado) |
| POST | `/api/users/` | Sí | Crear usuario |
| GET | `/api/users/{id}/` | Sí | Obtener detalle de un usuario |
| PUT | `/api/users/{id}/` | Sí | Actualizar usuario (completo) |
| PATCH | `/api/users/{id}/` | Sí | Actualizar usuario (parcial) |
| DELETE | `/api/users/{id}/` | Sí | Eliminar usuario |

---

## Estructura del proyecto

```
proyecto-base/
├── app/
│   ├── apps/
│   │   ├── auths/              # JWT, perfil propio (auth/me)
│   │   │   └── user/           # Login, refresh, blacklist, me
│   │   └── models/
│   │       └── user/           # Modelo User custom + CRUD API
│   ├── core/
│   │   ├── tests/              # Tests API (auth, users, health)
│   │   ├── settings/
│   │   │   ├── base.py         # Configuración base
│   │   │   ├── local.py        # Desarrollo
│   │   │   └── prod.py         # Producción (Railway)
│   │   ├── urls.py
│   │   └── docs.py             # Configuración de Swagger
│   ├── utils/                  # Permisos, paginación, excepciones
│   ├── .agents/skills/         # Skills de IA para agentes (Django)
│   ├── requirements/
│   │   ├── base.txt            # Runtime (prod)
│   │   ├── dev.txt             # + linters
│   │   └── prod.txt
│   ├── requirements.txt        # → dev.txt (compat)
│   └── manage.py
├── Dockerfile                  # Multi-stage: dev | production
├── .github/workflows/ci.yml    # Lint + migrate + health probe
├── AGENTS.md                   # Convenciones para agentes IA
├── docker-compose.yml
├── docker-compose.dev.yml      # Hot reload opcional (no auto-carga)
├── railway.toml
├── .env.dev-exemple
└── README.md
```

---

## Comandos útiles

### Migraciones

```bash
docker-compose exec web python manage.py migrate
```

### Crear superusuario

```bash
docker-compose exec web python manage.py createsuperuser
```

### Agregar una nueva app al proyecto

Reemplaza `<nombre>` con el nombre de tu aplicación:

```bash
docker-compose exec web python manage.py startapp <nombre> apps/models/<nombre>
```

Luego regístrala en `core/settings/base.py` → `LOCAL_APPS`.

### Generar backup de la base de datos

```bash
docker-compose exec web python manage.py dbbackup
```

### Ver logs del servidor

```bash
docker-compose logs -f web
```

### Reiniciar base de datos (desarrollo)

Si migraste desde una versión anterior con apps eliminadas y quedaron tablas huérfanas:

```bash
docker compose down -v
docker compose up -d --build
docker compose exec web python manage.py migrate
```

> Postgres usa el volumen `pgdata`, imagen `postgres:16-bookworm` (locales UTF-8) y healthcheck. El servicio `web` espera a que la BD esté lista antes de arrancar. Los scripts de arranque (`wait_for_db`, entrypoint) viven en `/usr/local/bin/` para no romperse con bind mounts en Windows.

**Logs esperados (no son errores):**
- `PostgreSQL ... Skipping initialization` → el volumen `pgdata` ya existe (normal al reiniciar).
- `No migrations to apply` → la BD ya está al día.

**Menos ruido en logs:** Postgres usa `log_min_messages=warning`; en dev el servidor es `gunicorn --reload` (no `runserver`). Para ver reintentos de BD: `WAIT_DB_VERBOSE=1` en `.env.dev`.

### Collectstatic en desarrollo

Por defecto **no** se ejecuta en cada arranque (arranque más rápido). Para forzarlo:

```bash
# En .env.dev
COLLECT_STATIC=1
```

---

## Linters y calidad de código

El proyecto usa **Flake8**, **Black** e **isort**. El flujo recomendado es:

### 1. Ordenar importaciones con isort

```bash
# Ver cambios sin aplicar
docker-compose exec web isort . --diff

# Aplicar cambios
docker-compose exec web isort .
```

### 2. Formatear código con Black

```bash
# Ver cambios sin aplicar
docker-compose exec web black . --diff

# Aplicar cambios
docker-compose exec web black .
```

### 3. Verificación final (CI)

Antes de commit:

```bash
docker compose exec web flake8 .
docker compose exec web black . --check
docker compose exec web isort . --check-only
```

En CI (GitHub Actions) corre automáticamente el workflow `.github/workflows/ci.yml`.

---

## CI (GitHub Actions)

Cada push/PR a `master` o `main` ejecuta `.github/workflows/ci.yml`:

- `flake8`, `black --check`, `isort --check-only`
- `python manage.py check` y `check --deploy` (prod settings)
- `python manage.py test core` (18 tests API/auth)
- Build imagen `production` + smoke test `GET /health`
- Probe HTTP dev en `GET /health`

Reproduce localmente:

```bash
cp .env.dev-exemple .env.dev
docker compose build web
docker compose up -d web-db
docker compose run --rm --no-deps --entrypoint flake8 web .
docker compose run --rm --no-deps --entrypoint black web . --check
docker compose run --rm --no-deps --entrypoint isort web . --check-only
docker compose run --rm --no-deps --entrypoint python web manage.py check
```

---

## Despliegue en producción (Railway)

Railway construye el `Dockerfile` de la raíz (target `production`). Producción usa `core/settings/prod.py`:

- `DEBUG=False`
- Archivos en **Cloudinary**, estáticos con **WhiteNoise**
- Base de datos vía `DATABASE_URL` (Postgres vinculado)
- `healthcheck.railway.app` permitido en `ALLOWED_HOSTS`

### Arquitectura de despliegue

```
GitHub push
    → Railway build (Dockerfile · target production)
    → preDeployCommand: migrate
    → wait_for_db (DATABASE_URL)
    → collectstatic + gunicorn ($PORT)
    → healthcheck GET /health
    → proyecto-base-production.up.railway.app
```

### Railway — configuración mínima

**Build:** Root Directory vacío · Dockerfile Path = `Dockerfile`

Variables detalladas en [Variables de entorno → Producción (Railway)](#producción-railway). Mínimo:

| Variable | Valor |
|---|---|
| `SECRET_KEY` | clave segura (50+ caracteres) |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
| `CLOUDINARY_*` | si usas media en prod |

Opcional: `CORS_ALLOWED_ORIGINS`, `ALLOWED_HOSTS`, `PRODUCTION=1`.

`RAILWAY_PUBLIC_DOMAIN` se añade automáticamente a CORS y CSRF si Railway lo inyecta.

**Networking:** Generate Domain → probar `https://<tu-app>.up.railway.app/health`

---

## Skills para agentes IA

El proyecto incluye skills en `app/.agents/skills/` (fuente: [vintasoftware/django-ai-plugins](https://github.com/vintasoftware/django-ai-plugins)):

| Skill | Uso |
|---|---|
| `django-expert` | Modelos, vistas, DRF, tests, despliegue |
| `cdrf-expert` | ViewSets, MRO, hooks de DRF (`perform_create`, etc.) |
| `django-safe-migration` | Migraciones PostgreSQL sin downtime |
| `docker-patterns` | Dockerfile, Compose, healthchecks, seguridad |
| `proyecto-base-docker` | Convenciones Docker de este repositorio |

---

## Licencia

Ver archivo [LICENSE](LICENSE).
