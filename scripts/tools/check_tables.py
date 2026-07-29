import psycopg2
conn = psycopg2.connect("postgresql://geo:geo@localhost:5432/geo_engine")
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
tables = cur.fetchall()
for t in tables:
    print(t[0])
print(f"Total tables: {len(tables)}")
conn.close()
