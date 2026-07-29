import psycopg2
conn = psycopg2.connect("postgresql://geo:geo@localhost:5432/geo_engine")
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name IN ('hashed_password', 'password_hash')")
cols = [r[0] for r in cur.fetchall()]
print("Password columns: " + str(cols))
if "hashed_password" in cols and "password_hash" in cols:
    cur.execute("ALTER TABLE users DROP COLUMN password_hash")
    cur.execute("ALTER TABLE users RENAME COLUMN hashed_password TO password_hash")
    print("Renamed hashed_password -> password_hash")
elif "hashed_password" in cols:
    cur.execute("ALTER TABLE users RENAME COLUMN hashed_password TO password_hash")
    print("Renamed hashed_password -> password_hash (single)")
else:
    print("Already password_hash")
conn.close()
