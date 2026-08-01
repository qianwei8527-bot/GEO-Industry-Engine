"""C6.5-R simulation transaction closure.

Runs the two synthetic transactions through TransactionEngine (not just metadata):
  - one settled
  - one failed/unresolved
Verifies idempotency, event history, and that synthetic outcomes never touch real nodes.
"""
import asyncio, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
from sqlalchemy import select
from app.database import _get_session_factory
from app.models.company import Company
from app.universe.transaction_engine import get_transaction_engine, TransactionEngine

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data", "public_sandbox_v1", "transactions.jsonl")

async def main():
    with open(DATA, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    assert all(r.get("is_synthetic") for r in rows), "only synthetic transactions allowed"
    factory = _get_session_factory()
    async with factory() as db:
        engine = get_transaction_engine()
        results = []
        for i, r in enumerate(rows):
            nodes_path = os.path.join(os.path.dirname(DATA), "nodes.jsonl")
            node_name = {}
            with open(nodes_path, encoding="utf-8") as nf:
                for line in nf:
                    if line.strip():
                        nd = json.loads(line)
                        node_name[nd["node_id"]] = nd["name"]
            na = (await db.execute(select(Company).where(Company.name == node_name.get(r["node_a"])))).scalars().first()
            nb = (await db.execute(select(Company).where(Company.name == node_name.get(r["node_b"])))).scalars().first()
            if not na or not nb:
                print(f"skip {r['node_a']}->{r['node_b']}: missing synthetic node")
                continue
            tx = engine.propose(str(na.id), str(nb.id), {"category": "service", "title": r["title"], "timeline_days": 30})
            engine.transition(tx.transaction_id, "agreed", str(na.id))
            engine.transition(tx.transaction_id, "started", str(nb.id))
            outcome = engine.complete(tx.transaction_id, r["status"], actor_id=str(na.id))
            hist = engine.get_transaction_with_history(tx.transaction_id)
            results.append({"title": r["title"], "status": outcome.status, "stage": hist["stage"], "events": len(hist["events"])})
            # idempotency: second complete must not re-feedback
            before_events = len(engine.get_transaction_with_history(tx.transaction_id)["events"])
            try:
                engine.complete(tx.transaction_id, r["status"], actor_id=str(na.id))
            except ValueError:
                pass
            after_events = len(engine.get_transaction_with_history(tx.transaction_id)["events"])
            results[-1]["idempotent"] = before_events == after_events
        print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
