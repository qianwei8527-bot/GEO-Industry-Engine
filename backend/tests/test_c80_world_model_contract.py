"""C8.0 Vertical World Model Contract tests."""

import sys, uuid
from pathlib import Path as FsPath
sys.path.insert(0, "D:/GEO-Industry-Engine/backend")

import pytest
import yaml
from sqlalchemy import select

from app.database import _get_session_factory
from app.models.company import Company
from app.models.evidence import Evidence
from app.services.world_model_contract import (
    WorldModelContractService, WorldPackageValidator, canonical_hash,
)
from app.services.trust_foundation import TrustFoundationService
from app.services.evidence_claim import EvidenceClaimService

FIXTURE = FsPath(r"D:\GEO-Industry-Engine\config\universe\worlds\edu_tech_admission\1.0.0.yaml")


def _load_package():
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def _code(prefix="world"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


class TestWorldModelContract:
    async def _create_world_draft(self, db, package=None, version="1.0.0"):
        package = package or _load_package()
        code = _code()
        svc = WorldModelContractService()
        await svc.create_world(db, code, package["world"]["name"])
        await svc.create_draft(db, code, version, package, source_file=str(FIXTURE))
        return code, svc

    async def test_create_publish_and_immutable(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, svc = await self._create_world_draft(db)
            published = await svc.publish(db, code, "1.0.0", "system")
            assert published["published"] is True
            with pytest.raises(ValueError):
                await svc.publish(db, code, "1.0.0", "system")
            with pytest.raises(ValueError):
                await svc.create_draft(db, code, "1.0.0", _load_package())

    async def test_validator_rejects_duplicate_cycle_dangling(self):
        dup = _load_package()
        dup["concepts"].append({"code": "parent", "type": "actor", "name": "duplicate"})
        assert not WorldPackageValidator().validate(dup)["valid"]

        dangling = _load_package()
        dangling["relations"].append({"from": "parent", "to": "missing", "type": "precedes"})
        assert not WorldPackageValidator().validate(dangling)["valid"]

        cycle = _load_package()
        cycle["relations"].append({"from": "objective_choose", "to": "scenario_planning", "type": "precedes"})
        assert not WorldPackageValidator().validate(cycle)["valid"]

    async def test_config_hash_deterministic(self):
        a = canonical_hash(_load_package())
        b = canonical_hash(_load_package())
        assert a == b
        assert len(a) == 64

    async def test_old_version_preserved_after_new_draft(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, svc = await self._create_world_draft(db, version="1.0.0")
            await svc.publish(db, code, "1.0.0", "system")
            modified = _load_package()
            modified["world"]["name"] = "修改后的世界"
            await svc.create_draft(db, code, "2.0.0", modified, source_file="2.0.0.yaml")
            old = await svc.get_version(db, code, "1.0.0")
            assert old["world"]["name"] == "科技特长生升学规划"
            new = await svc.get_version(db, code, "2.0.0")
            assert new["world"]["name"] == "修改后的世界"
            diff = await svc.diff(db, code, "1.0.0", "2.0.0")
            assert diff["config_hash_changed"] is True

    async def test_binding_verified_requires_verified_evidence(self):
        factory = _get_session_factory()
        async with factory() as db:
            code, svc = await self._create_world_draft(db)
            company = (await db.execute(select(Company).limit(1))).scalars().first()
            if not company:
                return
            verified_ev = (await db.execute(
                select(Evidence).where(Evidence.entity_id == company.id, Evidence.truth_status == "verified").limit(1)
            )).scalars().first()
            if not verified_ev:
                ev = Evidence(
                    entity_id=company.id, entity_type="company",
                    claim="GEO 案例", source_url="https://universe.test/verified",
                    source_name="Registry", source_type="system_record", truth_status="observed",
                )
                db.add(ev)
                await db.commit()
                await db.refresh(ev)
                await TrustFoundationService().verify_evidence(
                    db, str(ev.id), str(uuid.uuid4()),
                    method="universe_record_crosscheck", result="approved"
                )
                verified_ev = ev
            with pytest.raises(ValueError):
                await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                         "role_provider", truth_status="verified", evidence_claim_ids=[])
            claim = await EvidenceClaimService().create_claim(
                db, str(verified_ev.id), "company", str(company.id), "provides_capability",
                "concept", "role_provider", claim_text="GEO 案例"
            )
            await EvidenceClaimService().verify_claim(db, claim["id"], str(uuid.uuid4()))
            ok = await svc.create_binding(db, code, "1.0.0", "company", str(company.id),
                                          "role_provider", truth_status="verified",
                                          evidence_claim_ids=[claim["id"]])
            assert ok["truth_status"] == "verified"
            assert ok["evidence_ids"] == [str(verified_ev.id)]

    async def test_same_node_two_worlds_different_roles(self):
        factory = _get_session_factory()
        async with factory() as db:
            company = (await db.execute(select(Company).limit(1))).scalars().first()
            if not company:
                return
            svc = WorldModelContractService()
            codes = []
            for role in ("role_provider", "parent"):
                package = _load_package()
                code = _code("tw")
                await svc.create_world(db, code, package["world"]["name"])
                await svc.create_draft(db, code, "1.0.0", package)
                binding = await svc.create_binding(db, code, "1.0.0", "company",
                                                   str(company.id), role)
                assert binding["concept_code"] == role
                codes.append(code)
            assert codes[0] != codes[1]
