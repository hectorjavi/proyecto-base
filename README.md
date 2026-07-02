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

## Instalación y puesta en marcha (desarrollo)

### 1. Configurar variables de entorno

Copia el archivo de ejemplo y ajusta los valores si es necesario:

```bash
cp .env.dev-exemple .env.dev
```

El archivo `.env.dev` contiene los siguientes valores por defecto listos para desarrollo local:

```env
# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Django
PRODUCTION=0
SECRET_KEY=generate-key-here_CHANGE-THIS

# PostgreSQL
DATABASE=postgres
POSTGRES_HOST=web-db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB_NAME=web_db
```

> **Nota:** Para producción, actualiza `SECRET_KEY`, las credenciales de Cloudinary y configura `PRODUCTION=1`.

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

### 4. Credenciales del administrador por defecto

Se crean automáticamente tras la primera migración (`post_migrate`):

```
Email:    test@gmail.com
Usuario:  test
Password: test
```

---

## API — Endpoints disponibles

Todos los endpoints (excepto login y refresh) requieren header `Authorization: Bearer <access_token>`.

### Autenticación (`/api/auth/`)

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/health/` | No | Liveness probe |
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
│   │   │   ├── user/           # Login, refresh, blacklist, me
│   │   │   └── group/          # Grupos (extensible)
│   │   └── models/
│   │       └── user/           # Modelo User custom + CRUD API
│   ├── core/
│   │   ├── settings/
│   │   │   ├── base.py         # Configuración base
│   │   │   ├── local.py        # Desarrollo
│   │   │   └── prod.py         # Producción (Railway)
│   │   ├── urls.py
│   │   └── docs.py             # Configuración de Swagger
│   ├── utils/                  # Permisos, paginación, excepciones
│   ├── .agents/skills/         # Skills de IA para agentes (Django)
│   ├── Dockerfile              # Multi-stage: dev | production
│   ├── requirements/
│   │   ├── base.txt            # Runtime (prod)
│   │   ├── dev.txt             # + linters
│   │   └── prod.txt
│   ├── requirements.txt        # → dev.txt (compat)
│   └── manage.py
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
- `python manage.py check` y `migrate`
- Probe HTTP a `GET /health/`

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

El entorno de producción se configura mediante la variable `PRODUCTION=1`. Railway construye la imagen con **target `production`** (sin linters). La configuración de producción (`core/settings/prod.py`) activa:

- `DEBUG=False`
- Almacenamiento de archivos en **Cloudinary**
- Archivos estáticos servidos con **WhiteNoise**
- Cookies seguras (HTTPS)
- CORS habilitado
- Base de datos vía `DATABASE_URL` (inyectada por Railway al vincular Postgres)

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
