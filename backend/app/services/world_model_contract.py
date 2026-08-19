"""C8.0 Vertical World Model Contract.

Vertical worlds are versioned semantic projections over Universal facts.
They never duplicate Node / Evidence / Reputation / Demand / Connection.
"""

import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import yaml
from sqlalchemy import select, delete

from app.models.world_model_contract import (
    VerticalWorld, VerticalWorldVersion, WorldConcept,
    WorldConceptRelation, WorldBinding, WorldBindingEvidence,
)
from app.models.company import Company
from app.models.provider import Provider
from app.models.evidence import Evidence
from app.models.evidence_claim import EvidenceClaim


def _load_contract_config() -> Dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        'config', 'universe', 'world_contract.yaml',
    )
    with open(p, encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def canonical_hash(package: Dict) -> str:
    canonical = yaml.safe_dump(package, sort_keys=True, allow_unicode=True)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


class WorldPackageValidator:
    def __init__(self):
        self.config = _load_contract_config()

    def validate(self, package: Dict) -> Dict:
        errors: List[str] = []
        world = package.get("world") or {}
        code = world.get("code", "")
        if not code or not str(code).replace("_", "").isalnum():
            errors.append("world.code must be alphanumeric underscore code")
        if not world.get("name"):
            errors.append("world.name is required")

        concepts = package.get("concepts") or []
        concept_codes: Dict[str, str] = {}
        for i, c in enumerate(concepts):
            ccode = c.get("code", "")
            ctype = c.get("type", "")
            if not ccode:
                errors.append(f"concept[{i}].code is required")
                continue
            if ccode in concept_codes:
                errors.append(f"duplicate concept code: {ccode}")
            if ctype not in self.config.get("concept_types", []):
                errors.append(f"invalid concept type {ctype} for {ccode}")
            concept_codes[ccode] = ctype

        legal_relations = self.config.get("relation_types", {})
        relations = package.get("relations") or []
        edges_precedes = []
        edges_belongs = []
        for i, r in enumerate(relations):
            rtype = r.get("type", "")
            frm = r.get("from", "")
            to = r.get("to", "")
            if rtype not in legal_relations:
                errors.append(f"relation[{i}] invalid type {rtype}")
            if frm not in concept_codes:
                errors.append(f"relation[{i}] dangling from: {frm}")
            if to not in concept_codes:
                errors.append(f"relation[{i}] dangling to: {to}")
            if frm in concept_codes and to in concept_codes and rtype in legal_relations:
                allowed_from = legal_relations[rtype].get("from", ["all"])
                allowed_to = legal_relations[rtype].get("to", ["all"])
                if "all" not in allowed_from and concept_codes[frm] not in allowed_from:
                    errors.append(f"relation[{i}] type {rtype} not allowed from {concept_codes[frm]}")
                if "all" not in allowed_to and concept_codes[to] not in allowed_to:
                    errors.append(f"relation[{i}] type {rtype} not allowed to {concept_codes[to]}")
            if rtype == "precedes":
                edges_precedes.append((frm, to))
            if rtype == "belongs_to":
                edges_belongs.append((frm, to))

        if self._has_cycle(edges_precedes):
            errors.append("precedes relations contain a cycle")
        if self._has_cycle(edges_belongs):
            errors.append("belongs_to relations contain a cycle")

        return {
            "valid": not errors,
            "errors": errors,
            "concept_count": len(concepts),
            "relation_count": len(relations),
            "config_hash": canonical_hash(package),
        }

    @staticmethod
    def _has_cycle(edges: List[tuple]) -> bool:
        graph: Dict[str, List[str]] = {}
        for frm, to in edges:
            if not frm or not to:
                continue
            graph.setdefault(frm, []).append(to)
        visiting = set()
        visited = set()

        def dfs(node: str) -> bool:
            if node in visiting:
                return True
            if node in visited:
                return False
            visiting.add(node)
            for nxt in graph.get(node, []):
                if dfs(nxt):
                    return True
            visiting.remove(node)
            visited.add(node)
            return False

        return any(dfs(n) for n in list(graph))


class WorldModelContractService:
    def __init__(self):
        self.validator = WorldPackageValidator()

    async def create_world(self, db, code: str, name: str, description: str = None) -> Dict:
        existing = (await db.execute(select(VerticalWorld).where(VerticalWorld.code == code))).scalars().first()
        if existing:
            raise ValueError("world code already exists")
        world = VerticalWorld(code=code, name=name, description=description)
        db.add(world)
        await db.commit()
        await db.refresh(world)
        return self._world_dict(world)

    async def create_draft(self, db, world_code: str, version: str, package: Dict,
                           source_file: str = None) -> Dict:
        world = (await db.execute(select(VerticalWorld).where(VerticalWorld.code == world_code))).scalars().first()
        if not world:
            raise ValueError("world not found")
        existing = (await db.execute(select(VerticalWorldVersion).where(
            VerticalWorldVersion.world_id == world.id,
            VerticalWorldVersion.version == version,
        ))).scalars().first()
        if existing:
            raise ValueError("version already exists")
        report = self.validator.validate(package)
        if not report["valid"]:
            raise ValueError("invalid world package: " + "; ".join(report["errors"]))

        wmeta = package.get("world") or {}
        vrow = VerticalWorldVersion(
            world_id=world.id,
            version=version,
            schema_version=wmeta.get("schema_version", "1.0"),
            world_name=wmeta.get("name", world.name),
            world_description=wmeta.get("description", world.description),
            config_hash=report["config_hash"],
            source_file=source_file,
        )
        db.add(vrow)
        await db.commit()
        await db.refresh(vrow)

        for c in package.get("concepts") or []:
            db.add(WorldConcept(version_id=vrow.id, code=c["code"], concept_type=c["type"],
                                name=c.get("name", c["code"]), description=c.get("description"),
                                constraints=c.get("constraints")))
        for r in package.get("relations") or []:
            db.add(WorldConceptRelation(version_id=vrow.id, relation_type=r["type"],
                                        from_concept=r["from"], to_concept=r["to"]))
        await db.commit()
        return await self.get_version(db, world_code, version)

    async def publish(self, db, world_code: str, version: str, publisher: str) -> Dict:
        vrow = await self._version_row(db, world_code, version)
        if vrow.is_published:
            raise ValueError("published version is immutable")
        vrow.is_published = True
        vrow.published_by = publisher
        vrow.published_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(vrow)
        return await self.get_version(db, world_code, version)

    async def get_version(self, db, world_code: str, version: str) -> Dict:
        vrow = await self._version_row(db, world_code, version)
        concepts = (await db.execute(select(WorldConcept).where(WorldConcept.version_id == vrow.id))).scalars().all()
        relations = (await db.execute(select(WorldConceptRelation).where(WorldConceptRelation.version_id == vrow.id))).scalars().all()
        world = await db.get(VerticalWorld, vrow.world_id)
        return {
            "world": {
                "id": str(world.id), "code": world.code,
                "name": vrow.world_name or world.name,
                "description": vrow.world_description or world.description,
                "status": world.status,
            },
            "version": vrow.version,
            "schema_version": vrow.schema_version,
            "config_hash": vrow.config_hash,
            "source_file": vrow.source_file,
            "published": vrow.is_published,
            "published_by": vrow.published_by,
            "published_at": vrow.published_at.isoformat() if vrow.published_at else None,
            "concepts": [
                {"code": c.code, "type": c.concept_type, "name": c.name, "description": c.description}
                for c in concepts
            ],
            "relations": [
                {"type": r.relation_type, "from": r.from_concept, "to": r.to_concept}
                for r in relations
            ],
        }

    async def compiled(self, db, world_code: str, version: str) -> Dict:
        data = await self.get_version(db, world_code, version)
        return {
            "world_code": world_code,
            "version": version,
            "config_hash": data["config_hash"],
            "concepts": {c["code"]: c for c in data["concepts"]},
            "relations": data["relations"],
        }

    async def diff(self, db, world_code: str, from_version: str, to_version: str) -> Dict:
        a = await self.compiled(db, world_code, from_version)
        b = await self.compiled(db, world_code, to_version)
        added = [c for c in b["concepts"] if c not in a["concepts"]]
        removed = [c for c in a["concepts"] if c not in b["concepts"]]
        return {
            "world_code": world_code,
            "from": from_version,
            "to": to_version,
            "config_hash_changed": a["config_hash"] != b["config_hash"],
            "concepts_added": added,
            "concepts_removed": removed,
            "relation_count_from": len(a["relations"]),
            "relation_count_to": len(b["relations"]),
        }

    async def create_binding(self, db, world_code: str, version: str, entity_type: str,
                             entity_id: str, concept_code: str, truth_status: str = "observed",
                             evidence_claim_ids: List[str] = None, rule_version: str = "1.0.0",
                             mapping_source: str = "manual", created_by: str = None) -> Dict:
        world = (await db.execute(select(VerticalWorld).where(VerticalWorld.code == world_code))).scalars().first()
        if not world:
            raise ValueError("world not found")
        vrow = await self._version_row(db, world_code, version)
        concept = (await db.execute(select(WorldConcept).where(
            WorldConcept.version_id == vrow.id,
            WorldConcept.code == concept_code,
        ))).scalars().first()
        if not concept:
            raise ValueError(f"concept not found: {concept_code}")

        await self._validate_entity(db, entity_type, entity_id)
        claim_ids = evidence_claim_ids or []
        if truth_status == "verified":
            claim_rows = await self._validate_claim_support(db, vrow, concept, entity_type, entity_id, claim_ids)
        else:
            claim_rows = []
            if truth_status not in ("observed", "pending_review", "synthetic"):
                raise ValueError("invalid binding truth_status")
        evidence_ids = [str(c.evidence_id) for c in claim_rows]

        existing = (await db.execute(select(WorldBinding).where(
            WorldBinding.world_id == world.id,
            WorldBinding.version_id == vrow.id,
            WorldBinding.entity_type == entity_type,
            WorldBinding.entity_id == entity_id,
            WorldBinding.concept_code == concept_code,
        ))).scalars().first()
        if existing:
            existing.truth_status = truth_status
            existing.evidence_ids = evidence_ids
            existing.rule_version = rule_version
            existing.mapping_source = mapping_source
            existing.created_by = created_by
            await db.commit()
            await db.refresh(existing)
            await db.execute(delete(WorldBindingEvidence).where(WorldBindingEvidence.binding_id == existing.id))
            for claim in claim_rows:
                db.add(WorldBindingEvidence(binding_id=existing.id, evidence_id=claim.evidence_id,
                                            evidence_claim_id=claim.id))
            if claim_rows:
                await db.commit()
            return self._binding_dict(existing)
        binding = WorldBinding(
            world_id=world.id, version_id=vrow.id, entity_type=entity_type,
            entity_id=entity_id, concept_code=concept_code, truth_status=truth_status,
            evidence_ids=evidence_ids, rule_version=rule_version,
            mapping_source=mapping_source, created_by=created_by,
        )
        db.add(binding)
        await db.commit()
        await db.refresh(binding)
        for claim in claim_rows:
            db.add(WorldBindingEvidence(binding_id=binding.id, evidence_id=claim.evidence_id,
                                        evidence_claim_id=claim.id))
        if claim_rows:
            await db.commit()
        return self._binding_dict(binding)

    async def _validate_claim_support(self, db, vrow, concept, entity_type, entity_id,
                                     claim_ids) -> List[EvidenceClaim]:
        if not claim_ids:
            raise ValueError("verified binding requires verified EvidenceClaim")
        now = datetime.now(timezone.utc)
        req_rel = (await db.execute(select(WorldConceptRelation).where(
            WorldConceptRelation.version_id == vrow.id,
            WorldConceptRelation.relation_type == "validates",
            WorldConceptRelation.to_concept == concept.code,
        ))).scalars().first()
        if not req_rel:
            provided = (await db.execute(select(WorldConceptRelation).where(
                WorldConceptRelation.version_id == vrow.id,
                WorldConceptRelation.relation_type == "provides",
                WorldConceptRelation.from_concept == concept.code,
            ))).scalars().all()
            for pr in provided:
                req_rel = (await db.execute(select(WorldConceptRelation).where(
                    WorldConceptRelation.version_id == vrow.id,
                    WorldConceptRelation.relation_type == "validates",
                    WorldConceptRelation.to_concept == pr.to_concept,
                ))).scalars().first()
                if req_rel:
                    break
        req_meta = None
        if req_rel:
            req_meta = (await db.execute(select(WorldConcept).where(
                WorldConcept.version_id == vrow.id,
                WorldConcept.code == req_rel.from_concept,
            ))).scalars().first()
        constraints = (req_meta.constraints if req_meta else None) or {}
        allowed_types = constraints.get("allowed_source_types") or []
        allowed_predicates = constraints.get("allowed_predicates") or []

        rows = []
        for cid in claim_ids:
            try:
                claim = await db.get(EvidenceClaim, uuid.UUID(str(cid)))
            except (ValueError, TypeError):
                raise ValueError(f"invalid evidence_claim id: {cid}")
            if not claim or claim.truth_status != "verified":
                raise ValueError(f"verified binding requires verified EvidenceClaim: {cid}")
            if claim.valid_until and claim.valid_until <= now:
                raise ValueError(f"claim expired: {cid}")
            if claim.valid_from and claim.valid_from > now:
                raise ValueError(f"claim not yet valid: {cid}")
            if claim.subject_type != entity_type or claim.subject_id != entity_id:
                raise ValueError(f"claim subject mismatch for binding: {cid}")
            if allowed_predicates and claim.predicate_code not in allowed_predicates:
                raise ValueError(f"claim predicate not allowed for {concept.code}: {claim.predicate_code}")
            if claim.object_code != concept.code:
                raise ValueError(f"claim object mismatch for {concept.code}: {claim.object_code}")
            ev = await db.get(Evidence, claim.evidence_id)
            if not ev or ev.truth_status != "verified":
                raise ValueError(f"verified binding requires verified Evidence: {claim.evidence_id}")
            if not ev.may_affect_real_metrics or not claim.may_affect_real_metrics:
                raise ValueError(f"real metrics boundary violated for claim: {cid}")
            if ev.expires_at and ev.expires_at <= now:
                raise ValueError(f"evidence expired: {ev.id}")
            if ev.effective_at and ev.effective_at > now:
                raise ValueError(f"evidence not yet effective: {ev.id}")
            if entity_type == "company" and str(ev.entity_id) != entity_id:
                raise ValueError(f"evidence entity mismatch: {ev.id}")
            if allowed_types and (ev.source_type or "") not in allowed_types:
                raise ValueError(f"evidence type not allowed for {concept.code}: {ev.source_type}")
            rows.append(claim)
        return rows

    async def _version_row(self, db, world_code: str, version: str) -> VerticalWorldVersion:
        world = (await db.execute(select(VerticalWorld).where(VerticalWorld.code == world_code))).scalars().first()
        if not world:
            raise ValueError("world not found")
        row = (await db.execute(select(VerticalWorldVersion).where(
            VerticalWorldVersion.world_id == world.id,
            VerticalWorldVersion.version == version,
        ))).scalars().first()
        if not row:
            raise ValueError("version not found")
        return row

    async def _validate_entity(self, db, entity_type: str, entity_id: str):
        try:
            uid = uuid.UUID(str(entity_id))
        except (ValueError, TypeError):
            return  # non-UUID nodes allowed as generic refs
        if entity_type == "company":
            row = await db.get(Company, uid)
            if not row:
                raise ValueError("company entity not found")
        elif entity_type == "provider":
            row = await db.get(Provider, uid)
            if not row:
                raise ValueError("provider entity not found")

    def _world_dict(self, w: VerticalWorld) -> Dict:
        return {"id": str(w.id), "code": w.code, "name": w.name,
                "description": w.description, "status": w.status}

    def _binding_dict(self, b: WorldBinding) -> Dict:
        return {
            "id": str(b.id), "world_id": str(b.world_id), "version_id": str(b.version_id),
            "entity_type": b.entity_type, "entity_id": b.entity_id,
            "concept_code": b.concept_code, "truth_status": b.truth_status,
            "evidence_ids": b.evidence_ids or [], "rule_version": b.rule_version,
            "mapping_source": b.mapping_source, "created_by": b.created_by,
        }


def get_world_model_contract_service() -> WorldModelContractService:
    return WorldModelContractService()
