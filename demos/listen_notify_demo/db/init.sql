-- Runs automatically on first cluster init because it's mounted into
-- /docker-entrypoint-initdb.d/ inside the postgres container.

CREATE TABLE IF NOT EXISTS jobs (
  id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  payload    JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
