# Proyecto Base — Django + PostgreSQL + Docker

API REST construida con Django 4.2, PostgreSQL y Docker. Incluye autenticación JWT, documentación Swagger, almacenamiento en AWS S3 y despliegue en Railway.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Django 4.2, Django REST Framework 3.15 |
| Base de datos | PostgreSQL (psycopg2) |
| Autenticación | JWT (djangorestframework-simplejwt) |
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

### 3. Acceder a la aplicación

| Recurso | URL |
|---|---|
| API Docs (Swagger) | http://localhost:8000/docs/ |
| Django Admin | http://localhost:8000/admin/ |
| PostgreSQL (externo) | `localhost:5436` |

### 4. Credenciales del administrador por defecto

```
Email:    test@gmail.com
Usuario:  test
Password: test
```

---

## Estructura del proyecto

```
proyecto-base/
├── app/
│   ├── apps/
│   │   ├── auths/          # Autenticación y usuarios
│   │   └── models/         # Modelos de la aplicación
│   ├── core/
│   │   ├── settings/
│   │   │   ├── base.py     # Configuración base
│   │   │   └── prod.py     # Configuración de producción
│   │   ├── urls.py
│   │   └── docs.py         # Configuración de Swagger
│   ├── utils/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── manage.py
├── db/
│   ├── Dockerfile
│   └── create.sql
├── docker-compose.yml
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

### Generar backup de la base de datos

```bash
docker-compose exec web python manage.py dbbackup
```

### Ver logs del servidor

```bash
docker-compose logs -f web
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

Estos tres comandos deben pasar sin errores antes de hacer commit:

```bash
docker-compose exec web flake8 .
docker-compose exec web black . --check
docker-compose exec web isort . --check-only
```

---

## Despliegue en producción (Railway)

El entorno de producción se configura mediante la variable `PRODUCTION=1`. La configuración de producción (`core/settings/prod.py`) activa:

- `DEBUG=False`
- Almacenamiento de archivos en **Cloudinary**
- Archivos estáticos servidos con **WhiteNoise**
- Cookies seguras (HTTPS)
- CORS habilitado

---

## Licencia

Ver archivo [LICENSE](LICENSE).
