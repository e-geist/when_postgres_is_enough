import os
import time
import random
import psycopg2

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
            print(f"[{application_name or 'worker'}] DB not ready (attempt {i+1}/{max_attempts}): {e}", flush=True)
            time.sleep(delay)
    raise last_err

WORKER_NAME = os.environ.get("WORKER_NAME", "worker")

CLAIM_SQL = '''
WITH next_jobs AS (
  SELECT id
  FROM jobs
  WHERE status = 'queued'
    AND run_at <= now()
    AND (locked_until IS NULL OR locked_until <= now())
  ORDER BY priority DESC, run_at, id
  FOR UPDATE SKIP LOCKED
  LIMIT 1
)
UPDATE jobs j
SET status = 'running',
    attempts = attempts + 1,
    locked_by = %s,
    locked_until = now() + interval '30 seconds'
FROM next_jobs
WHERE j.id = next_jobs.id
RETURNING j.id, j.payload::text;
'''

MARK_DONE_SQL = "UPDATE jobs SET status='done', locked_by=NULL, locked_until=NULL WHERE id=%s"

def claim_one(cur):
    cur.execute(CLAIM_SQL, (WORKER_NAME,))
    return cur.fetchone()

def mark_done(cur, job_id):
    cur.execute(MARK_DONE_SQL, (job_id,))

def work_loop():
    conn = connect_with_retries(application_name=WORKER_NAME)
    print(f"[{WORKER_NAME}] Connected. Starting loop...", flush=True)

    idle_streak = 0
    while True:
        with conn:
            with conn.cursor() as cur:
                row = claim_one(cur)
        if not row:
            idle_streak = min(idle_streak + 1, 20)
            time.sleep(0.2 * idle_streak)  # gentle backoff when idle
            continue

        idle_streak = 0
        job_id, payload_json = row
        print(f"[{WORKER_NAME}] Claimed job {job_id} payload={payload_json}", flush=True)

        # Simulate doing work
        time.sleep(random.uniform(1, 5))

        with conn:
            with conn.cursor() as cur:
                mark_done(cur, job_id)
        print(f"[{WORKER_NAME}] Done job {job_id}", flush=True)

if __name__ == "__main__":
    work_loop()
