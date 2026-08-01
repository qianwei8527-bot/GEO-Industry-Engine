"""C6.5 Public Sandbox importer — idempotent, facts only.

Creates Companies/Evidence/Capabilities/Events/Relationships from the fixed
snapshot. NEVER seeds Position/Reputation/Possibility/Connection: those are
computed by engines (see verify_public_sandbox.py).
Re-importing the same packet does not duplicate rows.
"""
import asyncio, json, os, sys, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from sqlalchemy import select
from app.database import _get_session_factory
from app.models.company import Company
from app.models.capability import Capability
from app.models.evidence import Evidence
from app.models.geo_event import GeoEvent
from app.models.relationship import Relationship as RelORM

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "public_sandbox_v1")


def load_jsonl(name):
    p = os.path.join(DATA_DIR, name + ".jsonl")
    if not os.path.exists(p): return []
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


async def import_once(db):
    counts = {"nodes": 0, "capabilities": 0, "evidence": 0, "events": 0, "relationships": 0}
    node_name_by_id = {r["node_id"]: r["name"] for r in load_jsonl("nodes")}
    for row in load_jsonl("nodes"):
        existing = (await db.execute(select(Company).where(Company.name == row["name"]))).scalars().first()
        if existing:
            continue
        company = Company(name=row["name"], description=f"节点来源 {row.get('source', '')}",
                          website=row.get("website"), headquarters=row.get("region"),
                          entity_type="company", geo_id=f"GEO-COMP-{uuid.uuid4().hex[:8].upper()}")
        db.add(company); counts["nodes"] += 1
    await db.commit()

    for row in load_jsonl("capabilities"):
        company = (await db.execute(select(Company).where(Company.name == node_name_by_id.get(row["node_id"], row["node_id"])))).scalars().first()
        if not company:
            # node_id is id, not name; resolve via nodes map
            company = (await db.execute(select(Company).where(Company.name == node_name_by_id.get(row["node_id"], row["node_id"])))).scalars().first()
        if not company: continue
        ex = (await db.execute(select(Capability).where(Capability.company_id == company.id,
                                                        Capability.name == row["name"]))).scalars().first()
        if not ex:
            db.add(Capability(company_id=company.id, name=row["name"], level=row.get("level", 1)))
            counts["capabilities"] += 1
    await db.commit()

    for row in load_jsonl("evidence"):
        company = (await db.execute(select(Company).where(Company.name == node_name_by_id.get(row["node_id"], row["node_id"])))).scalars().first()
        if not company: continue
        ex = (await db.execute(select(Evidence).where(Evidence.entity_id == company.id,
                                                      Evidence.claim == row.get("title", ""),
                                                      Evidence.source_url == row.get("source_url", "")))).scalars().first()
        if not ex:
            db.add(Evidence(entity_type="company", entity_id=company.id, claim=row.get("title", ""),
                            source_url=row.get("source_url", ""), source_name=row.get("source_name"),
                            source_type=row.get("evidence_type", "other"),
                            truth_status=row.get("truth_status", "observed"),
                            is_synthetic=row.get("is_synthetic", False),
                            may_affect_real_metrics=row.get("may_affect_real_metrics", True),
                            expires_at=None, confidence_level=0.5, verified=False))
            counts["evidence"] += 1
    await db.commit()

    for row in load_jsonl("events"):
        company = (await db.execute(select(Company).where(Company.name == node_name_by_id.get(row["node_id"], row["node_id"])))).scalars().first()
        if not company: continue
        ex = (await db.execute(select(GeoEvent).where(GeoEvent.title == row.get("title", ""),
                                                      GeoEvent.source_node_id == company.id))).scalars().first()
        if not ex:
            db.add(GeoEvent(event_type=row.get("event_type", "public_record"), title=row.get("title", ""),
                            description=row.get("description", ""), source_node_id=company.id,
                            source_node_type="company", impact_level="medium",
                            impact_score=row.get("impact_score", 0.5), source_agent="public_sandbox_import",
                            is_processed=True))
            counts["events"] += 1
    await db.commit()

    for row in load_jsonl("relationships"):
        a = (await db.execute(select(Company).where(Company.name == node_name_by_id.get(row["node_a"], row["node_a"])))).scalars().first()
        b = (await db.execute(select(Company).where(Company.name == node_name_by_id.get(row["node_b"], row["node_b"])))).scalars().first()
        if not a or not b: continue
        ex = (await db.execute(select(RelORM).where(RelORM.source_id == a.id, RelORM.target_id == b.id,
                                                    RelORM.relation_type == row.get("type", "partners_with")))).scalars().first()
        if not ex:
            db.add(RelORM(source_id=a.id, target_id=b.id, relation_type=row.get("type", "partners_with"),
                          weight=row.get("weight", 0.5)))
            counts["relationships"] += 1
    await db.commit()
    return counts


async def main():
    factory = _get_session_factory()
    async with factory() as db:
        c1 = await import_once(db)
        c2 = await import_once(db)
        print("import pass1:", c1)
        print("import pass2 (idempotent):", c2)
        assert all(v == 0 for v in c2.values()), "second import must add nothing"
        print("IDEMPOTENT OK")

if __name__ == "__main__":
    asyncio.run(main())
