import json
import os
import signal
import time
import psycopg2
from datetime import datetime, timezone

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "app")
DB_PASSWORD = os.getenv("DB_PASSWORD", "app")
CHANNEL = os.getenv("CHANNEL", "work_ready")
INTERVAL = float(os.getenv("INTERVAL_SECONDS", "2"))

_running = True

def _handle_sigterm(signum, frame):
    global _running
    _running = False

signal.signal(signal.SIGTERM, _handle_sigterm)
signal.signal(signal.SIGINT, _handle_sigterm)


def connect():
    backoff = 0.5
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
            )
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            return conn
        except Exception as e:
            print(f"[notifier] DB connect failed: {e}. Retrying...", flush=True)
            time.sleep(backoff)
            backoff = min(backoff * 2, 5)

def main():
    conn = connect()
    cur = conn.cursor()
    i = 0
    print(f"[notifier] Publishing to channel '{CHANNEL}' every {INTERVAL}s", flush=True)
    while _running:
        i += 1
        payload_obj = {
            "type": "demo",
            "message": "hello from notifier",
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        # 1) Insert a job row
        cur.execute(
            "INSERT INTO jobs (payload) VALUES (%s) RETURNING id",
            (json.dumps(payload_obj),),
        )
        job_id = cur.fetchone()[0]
        # 2) Notify listeners with the new id as payload (as text)
        cur.execute("SELECT pg_notify(%s, %s)", (CHANNEL, str(job_id)))
        print(f"[notifier] inserted job id={job_id} and notified", flush=True)
        time.sleep(INTERVAL)

    print("[notifier] Shutting down.")
    try:
        cur.close()
        conn.close()
    except Exception:
        pass

if __name__ == "__main__":
    main()
