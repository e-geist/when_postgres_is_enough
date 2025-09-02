# Postgres `SELECT ... FOR UPDATE SKIP LOCKED` demo (flat apps, no packages)

This version **removes packages entirely** to avoid `__init__.py` issues:
- Producer and worker each have a single `app.py` with everything inside (includes the former `common` helpers).
- Separate Dockerfiles and build contexts for producer and worker.

## Services
- **db**: Postgres 17 (`postgres:17-alpine`)
- **producer**: inserts 1000 jobs and exits
- **worker1** and **worker2**: same image & code; both run `worker/app.py`

## Run
```bash
docker compose up --build
```

Change job count:
```bash
docker compose run --rm producer python -u app.py --count 5000
```

Inspect:
```sql
SELECT status, count(*) FROM jobs GROUP BY 1;
```
