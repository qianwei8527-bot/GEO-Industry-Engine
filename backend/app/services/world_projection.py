"""C8.1-R Trusted World Projection with structured claim integrity."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select

from app.models.world_model_contract import (
    VerticalWorld, VerticalWorldVersion, WorldConcept,
    WorldConceptRelation, WorldBinding, WorldBindingEvidence,
)
from app.models.evidence_claim import EvidenceClaim
from app.models.demand_event import DemandEvent
from app.models.connection_candidate import ConnectionCandidate
from app.models.evidence import Evidence
from app.models.company import Company


def _weakest(truths: List[str]) -> str:
    if not truths:
        return "unknown"
    if "synthetic" in truths:
        return "synthetic"
    if all(t == "verified" for t in truths):
        return "verified"
    return "observed"


def _canonical_fact_hash(fact_type: str, fact_id: str, revision: str, payload: Dict) -> str:
    data = {"fact_type": fact_type, "fact_id": fact_id, "fact_revision": revision, **payload}
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:32]


class WorldProjectionService:
    async def project(self, db, world_code: str, world_version: str,
                      as_of: str = None, production_only: bool = False,
                      expected_source_manifest: Dict[str, str] = None) -> Dict:
        world = (await db.execute(select(VerticalWorld).where(VerticalWorld.code == world_code))).scalars().first()
        if not world:
            raise ValueError("world not found")
        vrow = (await db.execute(select(VerticalWorldVersion).where(
            VerticalWorldVersion.world_id == world.id,
            VerticalWorldVersion.version == world_version,
        ))).scalars().first()
        if not vrow:
            raise ValueError("version not found")

        concepts = (await db.execute(select(WorldConcept).where(WorldConcept.version_id == vrow.id))).scalars().all()
        bindings = (await db.execute(select(WorldBinding).where(WorldBinding.version_id == vrow.id))).scalars().all()
        links = (await db.execute(select(WorldBindingEvidence).where(
            WorldBindingEvidence.binding_id.in_([b.id for b in bindings] or [uuid.uuid4()])
        ))).scalars().all()
        demands = (await db.execute(select(DemandEvent))).scalars().all()
        connections = (await db.execute(select(ConnectionCandidate))).scalars().all()

        concept_map = {c.code: c for c in concepts}
        links_by_binding: Dict[str, List[WorldBindingEvidence]] = {}
        for l in links:
            links_by_binding.setdefault(str(l.binding_id), []).append(l)

        claim_ids = sorted({str(l.evidence_claim_id) for l in links if l.evidence_claim_id})
        claims = {}
        for cid in claim_ids:
            try:
                c = await db.get(EvidenceClaim, uuid.UUID(cid))
                if c:
                    claims[cid] = c
            except (ValueError, TypeError):
                pass
        evidence_ids = sorted({str(l.evidence_id) for l in links})
        evidence_rows = {}
        for eid in evidence_ids:
            try:
                ev = await db.get(Evidence, uuid.UUID(eid))
                if ev:
                    evidence_rows[eid] = ev
            except (ValueError, TypeError):
                pass

        projection_as_of = as_of or datetime.now(timezone.utc).isoformat()
        items: List[Dict] = []
        excluded: List[Dict] = []
        bound_entity_ids = set()
        bound_concepts = set()
        source_refs: List[Dict] = []
        ref_index: Dict[str, Dict] = {}

        def add_ref(fact_type: str, fact_id: str, revision: str, truth_status: str, payload: Dict):
            key = f"{fact_type}:{fact_id}"
            if key in ref_index:
                return
            chash = _canonical_fact_hash(fact_type, fact_id, revision, payload)
            ref = {
                "fact_type": fact_type,
                "fact_id": fact_id,
                "fact_revision": revision,
                "canonical_fact_hash": chash,
                "truth_status": truth_status,
            }
            ref_index[key] = ref
            source_refs.append(ref)

        for b in bindings:
            bound_entity_ids.add(b.entity_id)
            bound_concepts.add(b.concept_code)
            concept = concept_map.get(b.concept_code)
            linked = links_by_binding.get(str(b.id), [])
            linked_claims = [claims.get(str(l.evidence_claim_id)) for l in linked if l.evidence_claim_id]
            linked_claims = [c for c in linked_claims if c]
            truths = [b.truth_status] + [c.truth_status for c in linked_claims]
            for l in linked:
                ev = evidence_rows.get(str(l.evidence_id))
                if ev:
                    truths.append(ev.truth_status)
                    add_ref("evidence", str(ev.id), self._rev(ev.updated_at), ev.truth_status,
                            {"claim": ev.claim, "source_url": ev.source_url,
                             "source_type": ev.source_type, "verified_at": self._rev(ev.verified_at)})
            truth = _weakest(truths)
            claim_supported = bool(linked_claims)
            kind = "outcome_claim" if concept and concept.concept_type == "outcome" else "node_binding"
            item = {
                "id": f"binding:{b.id}",
                "kind": kind,
                "universal_fact_id": f"{b.entity_type}:{b.entity_id}",
                "entity_type": b.entity_type,
                "entity_id": b.entity_id,
                "concept_code": b.concept_code,
                "concept_type": concept.concept_type if concept else "unknown",
                "truth_status": truth,
                "claim_supported": claim_supported,
                "source_fact_ids": sorted([str(l.evidence_id) for l in linked]),
                "source_claim_ids": sorted([str(l.evidence_claim_id) for l in linked if l.evidence_claim_id]),
                "demand_event_ids": [],
                "connection_candidate_ids": [],
                "excluded": False,
                "reason": None,
            }
            if production_only:
                if truth != "verified":
                    item["excluded"] = True
                    item["reason"] = "not_verified"
                elif not claim_supported:
                    item["excluded"] = True
                    item["reason"] = "no_structured_claim"
                if item["excluded"]:
                    excluded.append(item)
                    continue
            items.append(item)

        for d in demands:
            key = (d.missing_capability or "").lower()
            matched_code = None
            for code, concept in concept_map.items():
                if key == code.lower() or key == concept.name.lower():
                    matched_code = code
                    break
            if not matched_code:
                continue
            truth = _weakest([d.truth_status])
            add_ref("demand", str(d.id), self._rev(d.updated_at), d.truth_status,
                    {"question_text": d.question_text, "missing_capability": d.missing_capability,
                     "outcome": d.outcome})
            item = {
                "id": f"demand:{d.id}",
                "kind": "demand_binding",
                "universal_fact_id": f"demand:{d.id}",
                "entity_type": d.actor_type,
                "entity_id": str(d.actor_id) if d.actor_id else str(d.id),
                "concept_code": matched_code,
                "concept_type": concept_map[matched_code].concept_type,
                "truth_status": truth,
                "claim_supported": truth == "verified",
                "source_fact_ids": [str(d.id)],
                "source_claim_ids": [],
                "demand_event_ids": [str(d.id)],
                "connection_candidate_ids": [],
                "excluded": False,
                "reason": None,
            }
            if production_only and truth != "verified":
                item["excluded"] = True
                item["reason"] = "not_verified"
                excluded.append(item)
                continue
            items.append(item)

        for c in connections:
            if c.target_node_id not in bound_entity_ids:
                continue
            concept = concept_map.get(c.connection_type) or concept_map.get("role_provider")
            eligible = (
                c.truth_status == "verified"
                and c.decision_scope == "production"
                and c.may_affect_real_metrics
            )
            add_ref("connection", str(c.id), self._rev(c.updated_at), c.truth_status,
                    {"target_node_id": c.target_node_id, "status": c.status,
                     "decision_scope": c.decision_scope, "outcome": c.outcome})
            item = {
                "id": f"connection:{c.id}",
                "kind": "connection",
                "universal_fact_id": f"connection:{c.id}",
                "entity_type": "connection",
                "entity_id": c.target_node_id,
                "concept_code": concept.code if concept else c.connection_type,
                "concept_type": concept.concept_type if concept else "unknown",
                "truth_status": c.truth_status,
                "claim_supported": False,
                "source_fact_ids": [str(c.id)],
                "source_claim_ids": [],
                "demand_event_ids": [str(c.demand_event_id)],
                "connection_candidate_ids": [str(c.id)],
                "connection_status": c.status,
                "decision_scope": c.decision_scope,
                "excluded": False,
                "reason": None,
            }
            if production_only and not eligible:
                item["excluded"] = True
                item["reason"] = "not_production_eligible"
                excluded.append(item)
                continue
            items.append(item)

        manifest_hash = hashlib.sha256(
            "\n".join(
                f"{r['fact_type']}|{r['fact_id']}|{r['fact_revision']}|{r['canonical_fact_hash']}|{r['truth_status']}"
                for r in sorted(source_refs, key=lambda x: (x["fact_type"], x["fact_id"]))
            ).encode()
        ).hexdigest()[:32]

        source_drift = []
        if expected_source_manifest:
            current = {r["fact_id"]: r["canonical_fact_hash"] for r in source_refs}
            for fid, old_hash in expected_source_manifest.items():
                if fid in current and current[fid] != old_hash:
                    source_drift.append({"fact_id": fid, "old_hash": old_hash, "new_hash": current[fid]})

        truth_dist: Dict[str, int] = {}
        for it in items:
            truth_dist[it["truth_status"]] = truth_dist.get(it["truth_status"], 0) + 1

        company_ids = set(str(x) for x in (await db.execute(select(Company.id))).scalars().all())
        unmapped_company_ids = sorted(company_ids - bound_entity_ids)
        unsupported = [b for b in bindings if b.truth_status == "verified" and not links_by_binding.get(str(b.id))]
        missing = [{"code": c.code, "type": c.concept_type} for c in concepts if c.code not in bound_concepts]

        coverage = {
            "concept_coverage": {"total": len(concepts), "bound": len(bound_concepts), "missing": len(missing)},
            "verified_binding_coverage": {
                "total": len(bindings),
                "verified": sum(1 for b in bindings if b.truth_status == "verified"),
                "claim_supported": sum(
                    1 for it in items if it["kind"] == "node_binding" and it["claim_supported"]
                ),
            },
            "evidence_coverage": {"distinct_evidence": len(evidence_rows), "linked_bindings": len(links_by_binding)},
            "demand_coverage": {
                "total": len(demands),
                "matched": sum(1 for it in items if it["kind"] == "demand_binding"),
            },
            "connection_coverage": {
                "total": len(connections),
                "production_eligible": sum(
                    1 for it in items
                    if it["kind"] == "connection" and not it["excluded"] and it["truth_status"] == "verified"
                ),
            },
            "unmapped_facts": {"companies": len(unmapped_company_ids), "sample_company_ids": unmapped_company_ids[:10]},
            "unsupported_bindings": len(unsupported),
            "missing_required_concepts": missing,
        }

        unknown = {
            "missing_required_concepts": missing,
            "unmapped_companies": unmapped_company_ids[:20],
            "note": "unknown is rule-computed; no model guessing.",
        }

        return {
            "world_code": world_code,
            "world_version": world_version,
            "config_hash": vrow.config_hash,
            "projection_as_of": projection_as_of,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "production_only": production_only,
            "source_manifest_hash": manifest_hash,
            "source_refs": source_refs,
            "source_drift": source_drift,
            "truth_status_distribution": truth_dist,
            "items": items,
            "excluded": excluded,
            "coverage": coverage,
            "unknown": unknown,
        }

    async def source_chain(self, db, world_code: str, world_version: str,
                           entity_id: str, concept_code: str) -> Dict:
        world = (await db.execute(select(VerticalWorld).where(VerticalWorld.code == world_code))).scalars().first()
        if not world:
            raise ValueError("world not found")
        vrow = (await db.execute(select(VerticalWorldVersion).where(
            VerticalWorldVersion.world_id == world.id,
            VerticalWorldVersion.version == world_version,
        ))).scalars().first()
        if not vrow:
            raise ValueError("version not found")
        binding = (await db.execute(select(WorldBinding).where(
            WorldBinding.version_id == vrow.id,
            WorldBinding.entity_id == entity_id,
            WorldBinding.concept_code == concept_code,
        ))).scalars().first()
        if not binding:
            raise ValueError("binding not found")
        links = (await db.execute(select(WorldBindingEvidence).where(
            WorldBindingEvidence.binding_id == binding.id
        ))).scalars().all()
        chain = []
        for l in links:
            ev = await db.get(Evidence, l.evidence_id)
            claim = await db.get(EvidenceClaim, l.evidence_claim_id) if l.evidence_claim_id else None
            chain.append({
                "evidence_claim": {
                    "id": str(claim.id) if claim else None,
                    "predicate_code": claim.predicate_code if claim else None,
                    "object_code": claim.object_code if claim else None,
                    "subject_id": claim.subject_id if claim else None,
                    "truth_status": claim.truth_status if claim else None,
                    "verification_method": claim.verification_method if claim else None,
                    "verified_by": claim.verified_by if claim else None,
                    "verified_at": claim.verified_at.isoformat() if claim and claim.verified_at else None,
                } if claim else None,
                "evidence": {
                    "id": str(ev.id) if ev else None,
                    "claim": ev.claim if ev else None,
                    "source_url": ev.source_url if ev else None,
                    "source_type": ev.source_type if ev else None,
                    "truth_status": ev.truth_status if ev else None,
                    "may_affect_real_metrics": ev.may_affect_real_metrics if ev else None,
                    "verified_at": ev.verified_at.isoformat() if ev and ev.verified_at else None,
                    "expires_at": ev.expires_at.isoformat() if ev and ev.expires_at else None,
                } if ev else None,
            })
        return {
            "world_concept": {"code": concept_code},
            "binding": {
                "id": str(binding.id), "entity_id": binding.entity_id,
                "truth_status": binding.truth_status, "rule_version": binding.rule_version,
            },
            "chain": chain,
        }

    @staticmethod
    def _rev(value) -> str:
        if not value:
            return ""
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)


def get_world_projection_service() -> WorldProjectionService:
    return WorldProjectionService()
