import os
import time
import json
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "appdb")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")

DSN = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

def wait_for_db(max_wait=60):
    start = time.time()
    while True:
        try:
            with psycopg2.connect(DSN) as conn:
                conn.cursor().execute("SELECT 1")
            print("Database is ready.")
            return
        except Exception as e:
            if time.time() - start > max_wait:
                raise
            print("Waiting for database...", str(e))
            time.sleep(2)

def reset_table():
    # Truncate for idempotency when re-running the container
    with psycopg2.connect(DSN) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE orders RESTART IDENTITY;")
        conn.commit()

def seed_data():
    """
    Insert a handful of rows showing different JSONB shapes.
    We use psycopg2.extras.Json to adapt Python dicts to JSONB safely.
    """
    orders = [
        {
            "status": "pending",
            "customer_id": "CUST-001",
            "attrs": {
                "source": "web",
                "amount": 19.99,
                "gift": False,
                "currency": "USD",
                "items": [
                    {"sku": "BOOK-1", "category": "book", "qty": 1},
                    {"sku": "PEN-1", "category": "stationery", "qty": 2}
                ]
            }
        },
        {
            "status": "shipped",
            "customer_id": "CUST-002",
            "attrs": {
                "source": "mobile",
                "amount": 120.50,
                "gift": True,
                "currency": "EUR",
                "meta": {"priority": "high"},
                "items": [
                    {"sku": "HEADPHONES-1", "category": "electronics", "qty": 1}
                ]
            }
        },
        {
            "status": "processing",
            "customer_id": "CUST-001",
            "attrs": {
                "source": "web",
                "amount": 45.00,
                "gift": False,
                "currency": "USD",
                "notes": "Deliver after 6pm."
            }
        },
        {
            "status": "shipped",
            "customer_id": "CUST-003",
            "attrs": {
                "source": "api",
                "amount": 7.95,
                "gift": True,
                "currency": "GBP",
                "items": [
                    {"sku": "CHOC-1", "category": "food", "qty": 3},
                    {"sku": "BOOK-2", "category": "book", "qty": 1}
                ]
            }
        }
    ]

    with psycopg2.connect(DSN) as conn, conn.cursor() as cur:
        for o in orders:
            cur.execute(
                """
                INSERT INTO orders (status, customer_id, attrs)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (o["status"], o["customer_id"], psycopg2.extras.Json(o["attrs"]))
            )
            new_id = cur.fetchone()[0]
            print(f"Inserted order id={new_id} for customer {o['customer_id']}")
        conn.commit()

def demo_queries():
    with psycopg2.connect(DSN) as conn:
        # Use a RealDictCursor for regular result sets (dict-like rows)
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            print("--- Basic extraction with ->> and type casts ---")
            cur.execute("""
                SELECT id, status, customer_id,
                       attrs->>'source' AS source,
                       (attrs->>'amount')::numeric AS amount
                FROM orders
                ORDER BY id;
            """)
            rows = cur.fetchall()
            for r in rows:
                print(dict(r))

            print("--- Containment query with @> (gift:true) ---")
            cur.execute("""
                SELECT count(*) FROM orders
                WHERE attrs @> '{"gift": true}';
            """)
            print("gift:true count =>", cur.fetchone()["count"])

            print("--- Key existence with ? and ?| ---")
            cur.execute("""
                SELECT id, attrs ? 'notes' AS has_notes,
                       attrs ?| array['meta','notes'] AS has_meta_or_notes
                FROM orders ORDER BY id;
            """)
            for r in cur.fetchall():
                print(dict(r))

            print("--- JSON path existence: any item category == 'book' ---")
            cur.execute("""
                SELECT id, jsonb_path_exists(attrs, '$.items ? (@.category == "book")') AS has_book
                FROM orders ORDER BY id;
            """)
            for r in cur.fetchall():
                print(dict(r))

        # Use a *regular* cursor for EXPLAIN output to get tuple rows
        with conn.cursor() as cur_plain:
            print("--- Filter + sort via generated column 'amount' (btree index) ---")
            cur_plain.execute("""
                EXPLAIN ANALYZE
                SELECT id, amount FROM orders
                WHERE amount >= 10
                ORDER BY amount DESC
                LIMIT 3;
            """)
            plan_lines = [row[0] for row in cur_plain.fetchall()]
            plan = "\n".join(plan_lines)
            print(plan)

        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            print("--- Update with jsonb_set: set meta.updated_by and shipping timestamp ---")
            cur.execute("""
                UPDATE orders
                SET attrs = jsonb_set(
                              jsonb_set(attrs, '{meta,updated_by}', to_jsonb('app'::text), true),
                              '{shipping,shipped_at}',
                              to_jsonb(now()::timestamptz),
                              true
                            )
                WHERE status = 'shipped'
                RETURNING id, attrs->'meta' AS meta, attrs->'shipping' AS shipping;
            """)
            for r in cur.fetchall():
                print({"id": r["id"], "meta": r["meta"], "shipping": r["shipping"]})

            conn.commit()

            print("--- Concatenate with || : add a tag without overwriting other keys ---")
            cur.execute("""
                UPDATE orders
                SET attrs = attrs || '{"tag":"promo-sep"}'::jsonb
                WHERE id = 1
                RETURNING id, attrs->>'tag' AS tag;
            """)
            print(dict(cur.fetchone()))

            print("--- Array update example: append to items (if present) ---")
            cur.execute("""
                UPDATE orders
                SET attrs = jsonb_set(
                    attrs,
                    '{items}',
                    COALESCE(attrs->'items', '[]'::jsonb) || to_jsonb(jsonb_build_object('sku','STICKER-1','category','swag','qty',1)),
                    true
                )
                WHERE id = 1
                RETURNING id, attrs->'items' AS items;
            """)
            print(dict(cur.fetchone()))

def main():
    wait_for_db()
    reset_table()
    seed_data()
    demo_queries()
    print("All done. JSONB demo complete.")

if __name__ == "__main__":
    main()