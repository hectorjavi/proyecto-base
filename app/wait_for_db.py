#!/usr/bin/env python
"""
Waits for the database to be ready before starting the application.

Connection priority:
  1. DATABASE_URL  — Railway / Heroku / any PaaS (injected automatically)
  2. Individual POSTGRES_* env vars — local docker-compose fallback

Uses psycopg2 keyword arguments when falling back to individual vars so that
passwords with special characters (@, /, #, ?) are handled correctly without
URL-encoding issues.
"""
import os
import sys
import time

import psycopg2

MAX_RETRIES = 60


def _connect():
    """Return an open psycopg2 connection using available env vars."""
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)

    # Use keyword args to safely handle passwords with special characters.
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", ""),
        dbname=os.environ.get("POSTGRES_DB_NAME", "postgres"),
    )


def wait_for_db() -> None:
    verbose = os.environ.get("WAIT_DB_VERBOSE", "0") == "1"
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Mask credentials for safe logging
        safe = database_url.split("@")[-1] if "@" in database_url else database_url
        print(f"Waiting for database at {safe} ...", flush=True)
    else:
        host = os.environ.get("POSTGRES_HOST", "localhost")
        port = os.environ.get("POSTGRES_PORT", "5432")
        print(f"Waiting for database at {host}:{port} ...", flush=True)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn = _connect()
            conn.close()
            print("Database is ready.", flush=True)
            return
        except psycopg2.OperationalError as exc:
            if verbose:
                print(
                    f"  [{attempt}/{MAX_RETRIES}] Not ready yet: {exc}",
                    flush=True,
                )
            time.sleep(1)

    print(
        f"ERROR: Database not ready after {MAX_RETRIES} attempts. Aborting.",
        flush=True,
    )
    sys.exit(1)


if __name__ == "__main__":
    wait_for_db()
