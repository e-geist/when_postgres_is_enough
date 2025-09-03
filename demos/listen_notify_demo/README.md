# Postgres LISTEN/NOTIFY – Full Demo (2 Python services + Docker Compose)

This demo spins up three containers:

- **postgres** (database)
- **listener** (Python service that `LISTEN`s)
- **notifier** (Python service that inserts a row and `NOTIFY`s)

## Quick start

```bash
docker compose up --build
```

You should see the **listener** printing notifications every few seconds as the **notifier** inserts rows and publishes the new `job id` via `pg_notify()`.

## Notes

- The NOTIFY payload is the inserted `job id` (well under the ~8KB limit). Use it to fetch real data from the `jobs` table.
- Change `INTERVAL_SECONDS` in `docker-compose.yml` to control how often notifications are sent.
- Change `CHANNEL` to isolate topics (letters, digits, underscore).
- Keep listener transactions short (example runs in autocommit).
- Optional check from host:
  ```bash
  psql "postgresql://app:app@localhost:5432/appdb" -c "SELECT count(*) FROM jobs;"
  ```
