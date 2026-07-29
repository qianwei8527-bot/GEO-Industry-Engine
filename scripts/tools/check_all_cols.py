import psycopg2
conn = psycopg2.connect("postgresql://geo:geo@localhost:5432/geo_engine")
cur = conn.cursor()

# Get all tables and their columns
cur.execute("""
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema='public' AND table_name NOT IN ('alembic_version')
    ORDER BY table_name, ordinal_position
""")
current_table = ""
for row in cur.fetchall():
    if row[0] != current_table:
        current_table = row[0]
        print("--- " + current_table + " ---")
    print("  " + row[1] + ": " + row[2])

conn.close()
