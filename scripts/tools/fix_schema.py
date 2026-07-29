import psycopg2
conn = psycopg2.connect("postgresql://geo:geo@localhost:5432/geo_engine")
conn.autocommit = True
cur = conn.cursor()

# Check companies columns
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='companies' ORDER BY ordinal_position")
cols = [r[0] for r in cur.fetchall()]
print("Companies columns:", cols)

# Check users.id type
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users'")
for r in cur.fetchall():
    print(f"users.{r[0]}: {r[1]}")

# Add missing owner_id
if "owner_id" not in cols:
    cur.execute("ALTER TABLE companies ADD COLUMN owner_id UUID")
    print("Added owner_id to companies")

# Fix users.id to UUID
try:
    cur.execute("ALTER TABLE users ALTER COLUMN id TYPE UUID USING id::uuid")
    print("Fixed users.id to UUID")
except Exception as e:
    print(f"users.id fix skipped: {e}")

conn.close()
print("Schema fixes complete")
