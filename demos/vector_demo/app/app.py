import os, time, psycopg2

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "appdb")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def wait_for_db():
    for i in range(120):
        try:
            with psycopg2.connect(DSN) as c:
                return
        except Exception:
            print(f"Waiting for DB... ({i+1})")
            time.sleep(2)
    raise RuntimeError("DB not ready in time.")

def main():
    wait_for_db()
    with psycopg2.connect(DSN) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SET vchordrq.probes = '8';")

            for t in ("items_cos", "items_l2"):
                cur.execute(f"SELECT COUNT(*) FROM {t};")
                print((t, cur.fetchone()[0]))

            print("\nCosine (768‑D): Top‑5 nearest to 'anchor'")
            cur.execute("""                SELECT id, label
                FROM items_cos
                WHERE label != 'anchor'
                ORDER BY embedding <=> (SELECT embedding FROM items_cos WHERE label='anchor')
                LIMIT 5;
            """ )
            for r in cur.fetchall():
                print(r)

            print("\nCosine (768‑D): Top‑5 within radius 0.01 of 'anchor'")
            cur.execute("""                SELECT id, label
                FROM items_cos
                WHERE embedding <<=>> sphere(
                    (SELECT embedding FROM items_cos WHERE label='anchor'),
                    0.01
                )
                    AND label != 'anchor'
                ORDER BY embedding <=> (SELECT embedding FROM items_cos WHERE label='anchor')
                LIMIT 5;
            """ )
            for r in cur.fetchall():
                print(r)
            # Count how many rows match the cosine radius
            cur.execute("""
                SELECT COUNT(*) FROM items_cos
                WHERE embedding <<=>> sphere(
                    (SELECT embedding FROM items_cos WHERE label='anchor'),
                    0.01
                )
                    AND label != 'anchor';
            """)
            print(("cosine_within_0.01_count", cur.fetchone()[0]))


            print("\nL2 (768‑D): Top‑5 nearest to 'anchor'")
            cur.execute("""                SELECT id, label
                FROM items_l2
                WHERE label != 'anchor'
                ORDER BY embedding <-> (SELECT embedding FROM items_l2 WHERE label='anchor')
                LIMIT 5;
            """ )
            for r in cur.fetchall():
                print(r)

            print("\nL2 (768‑D): Top‑5 within radius 0.20 of 'anchor'")
            cur.execute("""                SELECT id, label
                FROM items_l2
                WHERE embedding <<->> sphere(
                    (SELECT embedding FROM items_l2 WHERE label='anchor'),
                    0.20
                )
                    AND label != 'anchor'
                ORDER BY embedding <-> (SELECT embedding FROM items_l2 WHERE label='anchor')
                LIMIT 5;
            """ )
            for r in cur.fetchall():
                print(r)
            # Count how many rows match the L2 radius
            cur.execute("""
                SELECT COUNT(*) FROM items_l2
                WHERE embedding <<->> sphere(
                    (SELECT embedding FROM items_l2 WHERE label='anchor'),
                    0.20
                )
                    AND label != 'anchor';
            """)
            print(("l2_within_0.20_count", cur.fetchone()[0]))


    print("\nAll set.")

if __name__ == "__main__":
    main()
