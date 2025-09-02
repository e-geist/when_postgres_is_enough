import os
import signal
import sys
import time
import psycopg2

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "app")
DB_PASSWORD = os.getenv("DB_PASSWORD", "app")
CHANNEL = os.getenv("CHANNEL", "work_ready")

_running = True

def _handle_sigterm(signum, frame):
    global _running
    _running = False

signal.signal(signal.SIGTERM, _handle_sigterm)
signal.signal(signal.SIGINT, _handle_sigterm)

def valid_channel(name: str) -> bool:
    # allow only letters, digits, and underscores, as identifiers
    return name.replace("_", "a").isalnum()

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
            print(f"[listener] DB connect failed: {e}. Retrying...", flush=True)
            time.sleep(backoff)
            backoff = min(backoff * 2, 5)

def main():
    if not valid_channel(CHANNEL):
        print(f"Invalid channel name: {CHANNEL}", file=sys.stderr)
        sys.exit(2)

    conn = connect()
    cur = conn.cursor()
    cur.execute(f"LISTEN {CHANNEL};")
    print(f"[listener] Listening on channel '{CHANNEL}'", flush=True)

    # Simple poll loop (no busy CPU): check every 0.5s
    while _running:
        time.sleep(0.5)
        conn.poll()
        while conn.notifies:
            n = conn.notifies.pop(0)
            print(
                f"[listener] got NOTIFY: channel={n.channel} payload={n.payload} from pid={n.pid}",
                flush=True,
            )

    print("[listener] Shutting down.")
    try:
        cur.close()
        conn.close()
    except Exception:
        pass

if __name__ == "__main__":
    main()
