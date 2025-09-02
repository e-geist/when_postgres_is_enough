-- init.sql: VectorChord extension, schema, seed data, and ANN indexes (cosine + L2) with 768‑D vectors

-- 1) Extension
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;

-- 2) Cosine demo (768‑D)
DROP TABLE IF EXISTS items_cos;
CREATE TABLE items_cos (
  id        bigserial PRIMARY KEY,
  label     text,
  embedding vector(768)
);

-- Anchor (one-hot in first dim) + near points (first two dims set, rest zeros)
INSERT INTO items_cos (label, embedding) VALUES
('anchor',
  (SELECT ARRAY(SELECT CASE WHEN i=1 THEN 1::real ELSE 0::real END FROM generate_series(1,768) i))::vector),
('near1',
  (ARRAY[0.95,0.10]::real[] || array_fill(0::real, ARRAY[766]))::vector),
('near2',
  (ARRAY[0.92,0.18]::real[] || array_fill(0::real, ARRAY[766]))::vector),
('near3',
  (ARRAY[0.90,0.20]::real[] || array_fill(0::real, ARRAY[766]))::vector);

-- Random background points
INSERT INTO items_cos (label, embedding)
SELECT 'vec_' || i,
       (SELECT ARRAY(SELECT (random()*2 - 1)::real FROM generate_series(1,768)))::vector
FROM generate_series(1, 400) AS g(i);

-- vchordrq index for cosine
CREATE INDEX items_cos_vrq_idx
ON items_cos USING vchordrq (embedding vector_cosine_ops)
WITH (options = $$
[build.internal]
lists = [256]
spherical_centroids = true
build_threads = 4
$$);

-- 3) L2 demo (768‑D)
DROP TABLE IF EXISTS items_l2;
CREATE TABLE items_l2 (
  id        bigserial PRIMARY KEY,
  label     text,
  embedding vector(768)
);

-- Anchor + near points (no normalization for L2)
INSERT INTO items_l2 (label, embedding) VALUES
('anchor',
  (SELECT ARRAY(SELECT CASE WHEN i=1 THEN 1::real ELSE 0::real END FROM generate_series(1,768) i))::vector),
('near1',
  (ARRAY[0.90,0.10]::real[] || array_fill(0::real, ARRAY[766]))::vector),
('near2',
  (ARRAY[0.85,0.15]::real[] || array_fill(0::real, ARRAY[766]))::vector),
('near3',
  (ARRAY[0.80,0.20]::real[] || array_fill(0::real, ARRAY[766]))::vector);

-- Random background points
INSERT INTO items_l2 (label, embedding)
SELECT 'vec_' || i,
       (SELECT ARRAY(SELECT (random()*2 - 1)::real FROM generate_series(1,768)))::vector
FROM generate_series(1, 400) AS g(i);

-- vchordrq index for L2
CREATE INDEX items_l2_vrq_idx
ON items_l2 USING vchordrq (embedding vector_l2_ops)
WITH (options = $$
[build.internal]
lists = [256]
build_threads = 4
$$);
