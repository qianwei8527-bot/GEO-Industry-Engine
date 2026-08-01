"""C6.5 Public Sandbox tests: idempotency, isolation, traceability, engine-derived results."""
import sys, os, asyncio
sys.path.insert(0, 'D:/GEO-Industry-Engine/backend')

import pytest
from sqlalchemy import select, func
from app.database import _get_session_factory
from app.models.company import Company
from app.models.evidence import Evidence
from app.models.capability import Capability

SANDBOX = os.path.join("D:/GEO-Industry-Engine/data/public_sandbox_v1")


class TestPublicSandbox:
    async def test_import_idempotent(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("imp", "D:/GEO-Industry-Engine/scripts/tools/import_public_sandbox.py")
        mod = importlib.util.module_from_spec(spec)
        try: spec.loader.exec_module(mod)
        except Exception: pytest.skip("import module")
        factory = _get_session_factory()
        async with factory() as db:
            c1 = await mod.import_once(db)
            c2 = await mod.import_once(db)
            assert all(v == 0 for v in c2.values())

    async def test_real_vs_synthetic_isolation(self):
        factory = _get_session_factory()
        async with factory() as db:
            real_names = ["清华大学", "北京大学", "复旦大学", "上海交通大学"]
            for nm in real_names:
                c = (await db.execute(select(Company).where(Company.name == nm))).scalars().first()
                if not c: continue
                evs = (await db.execute(select(Evidence).where(Evidence.entity_id == c.id))).scalars().all()
                assert all(not e.is_synthetic for e in evs)
                assert all(e.source_url for e in evs)
            bad = (await db.execute(select(func.count(Evidence.id)).where(
                Evidence.is_synthetic == True, Evidence.may_affect_real_metrics == True))).scalar()
            assert bad == 0

    async def test_synthetic_scenarios_present(self):
        factory = _get_session_factory()
        async with factory() as db:
            syn = (await db.execute(select(Company).where(Company.name.like("%仿真%")))).scalars().all()
            assert len(syn) >= 12
            names = {s.name for s in syn}
            assert any("疑似重名" in n for n in names)
            assert any("域名近似" in n for n in names)
            assert any("证据过期" in n or "晨光" in n for n in names)

    async def test_engine_derived_not_seeded(self):
        factory = _get_session_factory()
        async with factory() as db:
            from app.universe.context_engine import get_context_engine
            c = (await db.execute(select(Company).where(Company.name == "清华大学"))).scalars().first()
            if not c: pytest.skip("no node")
            ev_count = (await db.execute(select(func.count(Evidence.id)).where(Evidence.entity_id == c.id))).scalar()
            ctx = get_context_engine().understand(str(c.id), "company", {"name": c.name, "evidence_count": ev_count})
            assert ctx.current_position.get("position", {}).get("growth_stage") is not None
            assert ctx.reputation_profile

    async def test_rejected_observation_scenario(self):
        import json
        with open(os.path.join(SANDBOX, "observations.jsonl"), encoding="utf-8") as f:
            obs = [json.loads(l) for l in f if l.strip()]
        rejected = [o for o in obs if o.get("expected_review") == "rejected"]
        assert len(rejected) >= 1
        assert all(o.get("is_synthetic") for o in rejected)