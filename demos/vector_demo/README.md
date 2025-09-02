# VectorChord demo (768‑D, init.sql + simple app)

This variant uses **768‑dimensional vectors** for both cosine and L2 tables.

## What it includes
- Postgres + VectorChord, init via `/docker-entrypoint-initdb.d/init.sql`
- Two tables: `items_cos` (cosine) and `items_l2` (L2), each `vector(768)`
- Seed data: an `anchor`, a few `near*` vectors (first two dims), plus 400 random rows per table
- `vchordrq` indexes with appropriate opclasses
- App that prints top‑k and radius‑filtered examples (id, label only)

## Run

```bash
docker compose up --build
docker logs -f vchord-app
```

To re-run init.sql:
```bash
docker compose down -v
docker compose up --build
```

Notes:
- Probe count set to `8` for the demo; tune as needed.
- Cosine radius `0.25` and L2 radius `0.5` still include the `near*` examples in 768‑D.
