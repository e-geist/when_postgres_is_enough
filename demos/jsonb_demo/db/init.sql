-- Schema + indexes + constraints for a JSONB-heavy table
CREATE TABLE IF NOT EXISTS orders (
  id            BIGSERIAL PRIMARY KEY,
  created_at    timestamptz NOT NULL DEFAULT now(),
  status        text        NOT NULL,
  customer_id   text        NOT NULL,
  attrs         jsonb       NOT NULL DEFAULT '{}'::jsonb,

  -- Generated columns give typed, indexable views over JSONB
  amount        numeric     GENERATED ALWAYS AS ((attrs->>'amount')::numeric) STORED,
  gift          boolean     GENERATED ALWAYS AS ((attrs->>'gift')::boolean) STORED,
  source        text        GENERATED ALWAYS AS (attrs->>'source') STORED
);

-- Basic JSONB sanity checks
ALTER TABLE orders
  ADD CONSTRAINT attrs_is_object CHECK (jsonb_typeof(attrs) = 'object');

-- If amount key exists, it must be a number
ALTER TABLE orders
  ADD CONSTRAINT amount_is_number_if_present
  CHECK (NOT (attrs ? 'amount') OR jsonb_typeof(attrs->'amount') = 'number');

-- Require a 'source' key to exist in attrs (demoing key presence constraint)
ALTER TABLE orders
  ADD CONSTRAINT attrs_has_source CHECK (attrs ? 'source');

-- Indexes
-- 1) Broad GIN index for containment/exists
CREATE INDEX IF NOT EXISTS idx_orders_attrs_gin
  ON orders USING GIN (attrs);

-- 2) Expression/Generated column indexes for targeted lookups & range scans
CREATE INDEX IF NOT EXISTS idx_orders_amount ON orders (amount);
CREATE INDEX IF NOT EXISTS idx_orders_source ON orders (source);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status);

-- 3) Optional partial index example: only shipped orders with gift flag
CREATE INDEX IF NOT EXISTS idx_orders_gift_shipped
  ON orders (id)
  WHERE status = 'shipped' AND gift IS TRUE;