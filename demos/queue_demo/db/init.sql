-- Minimal schema: no functions, no triggers
CREATE TABLE IF NOT EXISTS jobs (
  id            BIGSERIAL PRIMARY KEY,
  payload       JSONB NOT NULL,
  status        TEXT NOT NULL DEFAULT 'queued',      -- queued | running | done | failed
  priority      INT  NOT NULL DEFAULT 0,
  run_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  attempts      INT  NOT NULL DEFAULT 0,
  locked_by     TEXT,
  locked_until  TIMESTAMPTZ,
  last_error    TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS jobs_status_run_at_idx ON jobs (status, run_at);
CREATE INDEX IF NOT EXISTS jobs_locked_until_idx  ON jobs (locked_until);
CREATE INDEX IF NOT EXISTS jobs_queued_run_at_idx ON jobs (run_at) WHERE status = 'queued';
