#!/usr/bin/env python
"""
Wait for the database before starting the application.

Priority: DATABASE_URL (Railway/PaaS) → POSTGRES_* (local docker-compose).
"""
import os
import sys
import time

import psycopg2

MAX_RETRIES = int(os.environ.get("WAIT_DB_MAX_RETRIES", "60"))


def _connect():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
        dbname=os.environ.get("POSTGRES_DB_NAME", "postgres"),
    )


def wait_for_db() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url and not os.environ.get("POSTGRES_HOST"):
        print("ERROR: Set DATABASE_URL or POSTGRES_HOST.", flush=True)
        sys.exit(1)

    if database_url:
        safe = database_url.split("@")[-1] if "@" in database_url else database_url
        print(f"Waiting for database at {safe} ...", flush=True)
    else:
        host = os.environ.get("POSTGRES_HOST", "localhost")
        port = os.environ.get("POSTGRES_PORT", "5432")
        print(f"Waiting for database at {host}:{port} ...", flush=True)

    verbose = os.environ.get("WAIT_DB_VERBOSE", "0") == "1"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn = _connect()
            conn.close()
            print("Database is ready.", flush=True)
            return
        except psycopg2.OperationalError as exc:
            if verbose:
                print(f"  [{attempt}/{MAX_RETRIES}] {exc}", flush=True)
            time.sleep(1)

    print(f"ERROR: Database not ready after {MAX_RETRIES} attempts.", flush=True)
    sys.exit(1)


if __name__ == "__main__":
    wait_for_db()
