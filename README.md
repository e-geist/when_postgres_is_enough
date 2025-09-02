# When Postgres Is Enough

Code and slides for a practical tour of solving *real* product needs with **just PostgreSQL**, before you reach for extra infrastructure. 

Topics include 

- **pub/sub (LISTEN/NOTIFY)**
- **job queues (SELECT … FOR UPDATE SKIP LOCKED)**
- **document storage (JSONB)**
- **vector storage with VectorChord**

> Built for the talk [“When Postgres Is Enough” at PyData Berlin 2025](https://cfp.pydata.org/berlin2025/talk/FDBZSR/).

---

## What you’ll learn

- **Pub/Sub with LISTEN/NOTIFY**: lightweight eventing without Kafka
- **Distributed work queues**: safe concurrent processing with `SELECT … FOR UPDATE SKIP LOCKED`
- **Document storage with JSONB**: storage and retrieval of schemaless data
- **Vector storage with VectorChord**: storage, retrieval and approximate nearest-neighbor search of vectorized data

Each example shows:
- Minimal schema + indices
- A tiny Python client (psycopg2) to produce/consume data
- Docker Compose (or a one-liner) for repeatable runs

---

## Prerequisites

- **Docker** & **Docker Compose**
- **psql** (handy for exploration)
- Optional: **Python 3.12+** if you want to run client scripts locally

---
## Repository layout

```bash
.
├─ demos/          # Self-contained, runnable demos (each has its own compose file)
└─ presentation/   # Slides / assets for the talk
```
- `demos/` contains one folder per topic; each demo is designed to run independently with Docker.
- `presentation/` hosts the materials used in the talk.

---
## Quickstart

Clone the repo and run whichever demo you want (each is self‑contained).

```bash
git clone https://github.com/e-geist/when_postgres_is_enough
cd when_postgres_is_enough
```

Replace `PATH_TO_DEMO` with a specific demo directory inside `demos/`.

```bash
# start one demo
cd demos/PATH_TO_DEMO
docker compose up --build

# in another terminal, connect to Postgres
psql postgres://postgres:postgres@localhost:5432/postgres
```

## Troubleshooting

- **Port 5432 already in use** – stop other local Postgres instances or map a different port.
- **psql can’t connect** – check the container is healthy: `docker ps` / `docker compose ps`.
- **Vector dimension mismatch** – the `vector(n)` column and any inserted/query vectors must use the same `n`.
- **Index not used / slow queries** – verify the right ops class and analyze after bulk inserts.

---

## Why is Postgres enough?

- Postgres is usually **already in your stack**.
- You can **ship sooner** by leaning on built‑ins and well‑supported extensions (and swap later if needed).

---

## License

If a `LICENSE` file appears in the repo, that’s the authoritative license. If not, please contact the author before reusing code or slides.
