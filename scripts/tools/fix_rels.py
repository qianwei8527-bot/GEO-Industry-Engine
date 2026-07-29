import psycopg2
conn = psycopg2.connect("postgresql://geo:geo@localhost:5432/geo_engine")
conn.autocommit = True
cur = conn.cursor()

# Fix relationships: rename strength -> weight, add missing columns
fixes = [
    "ALTER TABLE relationships RENAME COLUMN strength TO weight",
    "ALTER TABLE relationships ADD COLUMN IF NOT EXISTS description TEXT",
    "ALTER TABLE relationships ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()",
]
for sql in fixes:
    try:
        cur.execute(sql)
        print("OK: " + sql[:60])
    except Exception as e:
        print("SKIP: " + str(e)[:80])

# Verify
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='relationships' ORDER BY ordinal_position")
print("Relationships columns: " + str([r[0] for r in cur.fetchall()]))
conn.close()
