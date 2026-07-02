# syntax=docker/dockerfile:1
# Single Dockerfile — Railway (production) and docker-compose (dev).

# ── Shared base ───────────────────────────────────────────────────────────────
# Pin linux/amd64 digest (python:3.13.14-slim-bookworm). Re-pin on a schedule.
FROM python:3.13-slim-bookworm@sha256:129f9f5d5729767916d79f0021ba4fe56ff113332b08ef1213ecf529a9da7ebb AS base

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

COPY app/docker-entrypoint.sh app/wait_for_db.py /tmp/runtime-scripts/
RUN dos2unix /tmp/runtime-scripts/docker-entrypoint.sh /tmp/runtime-scripts/wait_for_db.py \
    && mv /tmp/runtime-scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh \
    && mv /tmp/runtime-scripts/wait_for_db.py /usr/local/bin/wait_for_db.py \
    && chmod +x /usr/local/bin/docker-entrypoint.sh /usr/local/bin/wait_for_db.py

# ── Development (docker-compose target: dev) ──────────────────────────────────
FROM base AS dev

RUN pip install --upgrade pip wheel

COPY app/requirements/base.txt app/requirements/dev.txt requirements/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements/dev.txt

COPY app/ .

RUN mkdir -p media staticfiles static \
    && chown -R appuser:appgroup /usr/src/app

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health')" || exit 1

ENTRYPOINT ["bash", "/usr/local/bin/docker-entrypoint.sh"]

# ── Production (Railway default — last stage) ─────────────────────────────────
FROM base AS production

RUN pip install --upgrade pip wheel

COPY app/requirements/base.txt requirements/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements/base.txt

COPY app/ .

RUN mkdir -p media staticfiles static \
    && chown -R appuser:appgroup /usr/src/app

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health')" || exit 1

ENTRYPOINT ["bash", "/usr/local/bin/docker-entrypoint.sh"]
