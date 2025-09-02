import argparse
import os
import time
from datetime import datetime, UTC
import psycopg2
from psycopg2.extras import execute_values, Json

def dsn_from_env():
    host = os.environ.get("POSTGRES_HOST", "localhost")
    db   = os.environ.get("POSTGRES_DB", "app")
    user = os.environ.get("POSTGRES_USER", "app")
    pw   = os.environ.get("POSTGRES_PASSWORD", "app")
    return f"host={host} dbname={db} user={user} password={pw}"

def connect_with_retries(application_name=None, max_attempts=60, delay=1.0):
    last_err = None
    for i in range(max_attempts):
        try:
            kwargs = {"dsn": dsn_from_env()}
            if application_name:
                kwargs["application_name"] = application_name
            conn = psycopg2.connect(**kwargs)
            conn.autocommit = False
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            return conn
        except Exception as e:
            last_err = e
            print(f"[{application_name or 'producer'}] DB not ready (attempt {i+1}/{max_attempts}): {e}", flush=True)
            time.sleep(delay)
    raise last_err

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1000, help="How many jobs to create")
    args = parser.parse_args()

    conn = connect_with_retries(application_name="producer")
    print(f"[producer] Connected. Inserting {args.count} jobs...", flush=True)

    t0 = time.time()
    values = [(Json({"n": i, "note": "example payload"}), 0, datetime.now(UTC)) for i in range(args.count)]
    with conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                '''
INSERT INTO jobs (payload, priority, run_at)
VALUES %s
''',
                values,
                template="(%s, %s, %s)"
            )
    print(f"[producer] Inserted {args.count} jobs in {time.time() - t0:.2f}s", flush=True)

if __name__ == "__main__":
    main()
