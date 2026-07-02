FROM python:3.13-slim-bookworm

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies in a single layer and clean up cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    gcc \
    postgresql-client \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip wheel
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

# Convert Windows/Mac line endings to Unix in the entrypoint script
RUN dos2unix --newfile docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh \
    && chmod +x /usr/local/bin/docker-entrypoint.sh

# Create required directories with open permissions
RUN mkdir -p /usr/src/app/media/ \
             /usr/src/app/staticfiles/ \
             /usr/src/app/static/ \
    && chmod -R 777 /usr/src/app/media/ \
                    /usr/src/app/staticfiles/ \
                    /usr/src/app/static/

ENTRYPOINT ["bash", "/usr/local/bin/docker-entrypoint.sh"]
