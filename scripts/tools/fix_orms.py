import sys
base = r"D:\GEO-Industry-Engine\backend\app\models"

# Fix evidence.py
with open(base + r"\evidence.py", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("__tablename__ = \"evidences\"", "__tablename__ = \"evidence\"")
c = c.replace("target_id", "entity_id")
c = c.replace("confidence_level: Mapped[int]", "confidence_level: Mapped[float]")
c = c.replace("mapped_column(Integer, default=0)", "mapped_column(Float, default=0.0)")
# Add entity_type
old = "    id: Mapped[uuid.UUID]"
new = "    entity_type: Mapped[str] = mapped_column(String(32), default=\"company\")\n    id: Mapped[uuid.UUID]"
c = c.replace(old, new)
with open(base + r"\evidence.py", "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed evidence.py")

# Fix event.py
with open(base + r"\event.py", "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("occurred_at", "event_date")
c = c.replace("impact_level", "impact")
c = c.replace("impact: Mapped[int]", "impact: Mapped[str]")
c = c.replace("mapped_column(Integer, default=1)", "mapped_column(String(20), default=\"medium\")")
old = "    id: Mapped[uuid.UUID]"
new = "    entity_type: Mapped[str] = mapped_column(String(32), default=\"company\")\n    id: Mapped[uuid.UUID]"
c = c.replace(old, new)
c = c.replace("source_url: Mapped[str | None]", "source: Mapped[str | None]")
with open(base + r"\event.py", "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed event.py")

# Drop metadata_ column from entities (replaced by ext_metadata)
import psycopg2
conn = psycopg2.connect("postgresql://geo:geo@localhost:5432/geo_engine")
conn.autocommit = True
cur = conn.cursor()
try:
    cur.execute("ALTER TABLE entities DROP COLUMN IF EXISTS metadata_")
    print("Dropped entities.metadata_")
except:
    print("metadata_ already gone")
conn.close()

print("All ORM fixes complete")
