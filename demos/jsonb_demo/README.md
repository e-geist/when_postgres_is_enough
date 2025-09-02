# PostgreSQL JSONB Demo (Docker + Python)

A minimal, production-flavored demo showing how to:

- Use a `JSONB` column with **constraints**, **generated columns**, and **indexes**
- Insert Python dictionaries safely via `psycopg2`
- Query JSONB with operators (`@>`, `?`, `#>>`), **JSONPath**, and **generated columns**
- Update JSONB using `jsonb_set` and concatenation `||`

## Stack

- PostgreSQL **17-alpine**
- Python **3.12** + `psycopg2-binary`

## Quick Start

```bash
# from this folder
docker compose up --build
```

You’ll see the Python app wait for Postgres, seed a few rows, then run a series of demo queries and updates.

### What gets created

- Table: `orders(id, created_at, status, customer_id, attrs jsonb, amount generated, gift generated, source generated)`
- Constraints:
  - `attrs` must be a JSON object
  - If `amount` key exists in `attrs`, it must be numeric
  - `attrs` must contain a `source` key
- Indexes:
  - `GIN` on `attrs` for containment/exists queries
  - `btree` on generated `amount`, `source`, and on `status`
  - Partial index on shipped gifted orders

### Useful commands

Inspect data:
```bash
docker exec -it jsonb_demo_db psql -U postgres -d appdb -c "TABLE orders;"
```

Re-run the queries:
```bash
docker logs -f jsonb_demo_app
```

Stop:
```bash
docker compose down
```

## Notes

- Generated columns give you **typed, indexable** projections from `attrs`.
- The `jsonb_set` calls demonstrate **upserts** into nested structures (creating missing paths).
- If you plan to update JSON frequently at high rates, consider moving **hot fields** into regular columns.