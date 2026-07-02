# syntax=docker/dockerfile:1

# ── Shared base ───────────────────────────────────────────────────────────────
FROM python:3.13-slim-bookworm AS base

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# ── Shared runtime scripts (outside /usr/src/app — safe with bind mounts) ─────
COPY docker-entrypoint.sh wait_for_db.py /tmp/runtime-scripts/
RUN dos2unix /tmp/runtime-scripts/docker-entrypoint.sh /tmp/runtime-scripts/wait_for_db.py \
    && mv /tmp/runtime-scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh \
    && mv /tmp/runtime-scripts/wait_for_db.py /usr/local/bin/wait_for_db.py \
    && chmod +x /usr/local/bin/docker-entrypoint.sh /usr/local/bin/wait_for_db.py

# ── Development (linters + optional hot reload via docker-compose.dev.yml) ─────
FROM base AS dev

RUN pip install --upgrade pip wheel

COPY requirements/base.txt requirements/dev.txt requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt

COPY . .

RUN mkdir -p media staticfiles static \
    && chown -R appuser:appgroup /usr/src/app

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health/')" || exit 1

ENTRYPOINT ["bash", "/usr/local/bin/docker-entrypoint.sh"]

# ── Production (default target for Railway / plain docker build) ──────────────
FROM base AS production

RUN pip install --upgrade pip wheel

COPY requirements/base.txt requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

COPY . .

RUN mkdir -p media staticfiles static \
    && chown -R appuser:appgroup /usr/src/app

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health/')" || exit 1

ENTRYPOINT ["bash", "/usr/local/bin/docker-entrypoint.sh"]
