import psycopg2

def setup_postgres():
    # Try default postgres user first
    for attempt in [
        {"host": "localhost", "user": "postgres", "password": "postgres", "dbname": "postgres"},
        {"host": "localhost", "user": "postgres", "password": "admin", "dbname": "postgres"},
        {"host": "localhost", "dbname": "postgres"},  # Windows trust auth
    ]:
        try:
            conn = psycopg2.connect(**attempt)
            conn.autocommit = True
            cur = conn.cursor()
            print(f"Connected with: {attempt.get('user', 'trust')}")

            cur.execute("SELECT 1 FROM pg_roles WHERE rolname='geo'")
            if not cur.fetchone():
                cur.execute("CREATE ROLE geo WITH LOGIN PASSWORD 'geo' SUPERUSER")
                print("Created role: geo")
            else:
                print("Role geo already exists")

            cur.execute("SELECT 1 FROM pg_database WHERE datname='geo_engine'")
            if not cur.fetchone():
                cur.execute("CREATE DATABASE geo_engine OWNER geo")
                print("Created database: geo_engine")
            else:
                print("Database geo_engine already exists")

            conn.close()
            return True
        except Exception as e:
            print(f"Attempt failed: {type(e).__name__}: {e}")
            continue
    return False

if setup_postgres():
    print("PostgreSQL setup: OK")
else:
    print("PostgreSQL setup: FAILED - could not connect")
