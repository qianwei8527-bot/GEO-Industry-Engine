"""C8.2 World State Engine.

Deterministic, versioned, auditable vertical world state snapshots.
No synthetic scores; only counts, coverage and explicit formulas.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import yaml
from sqlalchemy import select

from app.models.world_state_snapshot import WorldStateSnapshot
from app.models.world_model_contract import VerticalWorld
from app.services.world_projection import WorldProjectionService

_SCOPES = ("production", "observation", "simulation")


def _load_config() -> Dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        'config', 'universe', 'world_state.yaml',
    )
    raw = open(p, encoding='utf-8').read()
    data = yaml.safe_load(raw) or {}
    data['config_hash'] = hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]
    return data


def _canonical_hash(payload: Dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()[:32]


class WorldStateService:
    def __init__(self):
        self.config = _load_config()

    async def generate(self, db, world_code: str, world_version: str,
                       state_scope: str = "production",
                       projection_as_of: str = None) -> Dict:
        if state_scope not in _SCOPES:
            raise ValueError("state_scope must be production/observation/simulation")
        projection = await WorldProjectionService().project(
            db, world_code, world_version, as_of=projection_as_of,
            production_only=(state_scope == "production"),
        )

        items = projection["items"]
        excluded = projection["excluded"]
        unknown = projection["unknown"]
        truth_dist = projection["truth_status_distribution"]
        source_manifest_hash = projection["source_manifest_hash"]

        if state_scope == "production":
            items = [i for i in items if i["truth_status"] == "verified"]
        elif state_scope == "observation":
            items = [i for i in items if i["truth_status"] in ("verified", "observed")]

        dimensions = self._aggregate(items, excluded, unknown, state_scope,
                                               projection["coverage"]["verified_binding_coverage"]["total"])
        gaps = self._gaps(items, excluded, unknown, state_scope)

        payload = {
            "world_code": world_code,
            "world_version": world_version,
            "config_hash": projection["config_hash"],
            "state_scope": state_scope,
            "projection_as_of": projection["projection_as_of"],
            "projection_manifest_hash": projection["source_manifest_hash"],
            "aggregation_rule_version": self.config.get("version", "1.0.0"),
            "aggregation_config_hash": self.config.get("config_hash"),
            "source_manifest_hash": source_manifest_hash,
            "dimensions": dimensions,
            "truth_distribution": truth_dist,
            "gaps": gaps,
            "unknown": unknown,
            "excluded_count": len(excluded),
        }
        snapshot_hash = _canonical_hash(payload)

        existing = (await db.execute(select(WorldStateSnapshot).where(
            WorldStateSnapshot.snapshot_hash == snapshot_hash
        ))).scalars().first()
        if existing:
            return self._to_dict(existing)

        world = (await db.execute(select(VerticalWorld).where(VerticalWorld.code == world_code))).scalars().first()
        if not world:
            raise ValueError("world not found")
        snapshot = WorldStateSnapshot(
            snapshot_id=str(uuid.uuid4()),
            world_id=world.id,
            world_code=world_code,
            world_version=world_version,
            config_hash=projection["config_hash"],
            state_scope=state_scope,
            projection_as_of=projection["projection_as_of"],
            projection_manifest_hash=projection["source_manifest_hash"],
            aggregation_rule_version=self.config.get("version", "1.0.0"),
            aggregation_config_hash=self.config.get("config_hash"),
            source_manifest_hash=source_manifest_hash,
            dimensions=dimensions,
            truth_distribution=truth_dist,
            gaps=gaps,
            unknown=unknown,
            excluded=excluded,
            snapshot_hash=snapshot_hash,
            generated_at=datetime.now(timezone.utc),
        )
        db.add(snapshot)
        await db.commit()
        await db.refresh(snapshot)
        return self._to_dict(snapshot)

    async def get(self, db, snapshot_id: str) -> Dict:
        snap = await self._get_snapshot(db, snapshot_id)
        return self._to_dict(snap)

    async def list_snapshots(self, db, limit: int = 50) -> List[Dict]:
        rows = (await db.execute(
            select(WorldStateSnapshot).order_by(WorldStateSnapshot.created_at.desc()).limit(limit)
        )).scalars().all()
        return [self._to_dict(r) for r in rows]

    async def summary(self, db, snapshot_id: str) -> Dict:
        snap = await self._get_snapshot(db, snapshot_id)
        dims = snap.dimensions or {}
        return {
            "snapshot_id": snap.snapshot_id,
            "world_code": snap.world_code,
            "world_version": snap.world_version,
            "state_scope": snap.state_scope,
            "snapshot_hash": snap.snapshot_hash,
            "is_stale": snap.is_stale,
            "summary": {
                "unique_nodes": dims.get("nodes", {}).get("unique_count"),
                "capability_supply": dims.get("capability_supply", {}).get("unique_pairs"),
                "verified_demands": dims.get("demand", {}).get("verified_count"),
                "completed_connections": dims.get("connection", {}).get("status", {}).get("completed"),
                "verified_outcomes": dims.get("outcome", {}).get("verified_count"),
                "gap_count": len(snap.gaps or []),
            },
        }

    async def concept_state(self, db, snapshot_id: str, concept_code: str) -> Dict:
        snap = await self._get_snapshot(db, snapshot_id)
        dims = snap.dimensions or {}
        supply = dims.get("capability_supply", {}).get("by_concept", {}).get(concept_code, 0)
        demand = dims.get("demand", {}).get("by_concept", {}).get(concept_code, 0)
        connections = dims.get("connection", {}).get("by_concept", {}).get(concept_code, {})
        gaps = [g for g in (snap.gaps or []) if g.get("concept_code") == concept_code]
        return {
            "concept_code": concept_code,
            "capability_supply": supply,
            "demand": demand,
            "connections": connections,
            "gaps": gaps,
        }

    async def gaps(self, db, snapshot_id: str) -> List[Dict]:
        snap = await self._get_snapshot(db, snapshot_id)
        return snap.gaps or []

    async def unknown_excluded(self, db, snapshot_id: str) -> Dict:
        snap = await self._get_snapshot(db, snapshot_id)
        return {"unknown": snap.unknown or {}, "excluded": snap.excluded or []}

    async def source_chain(self, db, snapshot_id: str, entity_id: str, concept_code: str) -> Dict:
        snap = await self._get_snapshot(db, snapshot_id)
        return await WorldProjectionService().source_chain(
            db, snap.world_code, snap.world_version, entity_id, concept_code
        )

    async def check_integrity(self, db, snapshot_id: str) -> Dict:
        snap = await self._get_snapshot(db, snapshot_id)
        current = await WorldProjectionService().project(
            db, snap.world_code, snap.world_version,
            as_of=snap.projection_as_of,
            production_only=(snap.state_scope == "production"),
        )
        old_hash = snap.source_manifest_hash
        new_hash = current["source_manifest_hash"]
        stale = old_hash != new_hash
        if stale:
            snap.is_stale = True
            await db.commit()
        return {
            "snapshot_id": snap.snapshot_id,
            "stale": stale,
            "old_source_manifest_hash": old_hash,
            "new_source_manifest_hash": new_hash,
            "source_drift": current["source_drift"],
        }

    # ---- aggregation ----

    def _aggregate(self, items: List[Dict], excluded: List[Dict],
                   unknown: Dict, state_scope: str, binding_total: int = 0) -> Dict:
        nodes = set()
        role_pairs = set()
        supply_pairs = set()
        supply_nodes = set()
        demand_ids = set()
        demand_by_concept: Dict[str, int] = {}
        demand_verified_by_concept: Dict[str, int] = {}
        claim_ids = set()
        evidence_ids = set()
        verified_evidence_ids = set()
        conn_by_status: Dict[str, int] = {}
        conn_by_concept: Dict[str, Dict] = {}
        outcome_by_truth: Dict[str, int] = {}
        completed_count = 0
        node_ids: List[str] = []
        role_binding_list: List[Dict] = []
        supply_pair_list: List[Dict] = []
        demand_id_list: List[str] = []
        evidence_id_list: List[str] = []
        claim_id_list: List[str] = []
        connection_id_list: List[Dict] = []
        outcome_id_list: List[Dict] = []

        for it in items:
            if it["kind"] == "node_binding":
                if it["entity_id"] not in nodes:
                    node_ids.append(it["entity_id"])
                nodes.add(it["entity_id"])
                pair = {"entity_id": it["entity_id"], "concept_code": it["concept_code"]}
                if (it["entity_id"], it["concept_code"]) not in role_pairs:
                    role_binding_list.append(pair)
                role_pairs.add((it["entity_id"], it["concept_code"]))
                if it["concept_type"] in ("capability", "role"):
                    if state_scope != "production" or (it["truth_status"] == "verified" and it.get("claim_supported")):
                        if (it["entity_id"], it["concept_code"]) not in supply_pairs:
                            supply_pair_list.append(pair)
                        supply_pairs.add((it["entity_id"], it["concept_code"]))
                        supply_nodes.add(it["entity_id"])
                if it.get("claim_supported"):
                    for cid in it.get("source_claim_ids") or []:
                        if cid not in claim_ids:
                            claim_id_list.append(cid)
                        claim_ids.add(cid)
                    for eid in it.get("source_fact_ids") or []:
                        if eid not in evidence_ids:
                            evidence_id_list.append(eid)
                        evidence_ids.add(eid)
                if it["truth_status"] == "verified":
                    verified_evidence_ids.update(it.get("source_fact_ids") or [])
            elif it["kind"] == "demand_binding":
                if it["id"] not in demand_ids:
                    demand_id_list.append(it["id"])
                demand_ids.add(it["id"])
                demand_by_concept[it["concept_code"]] = demand_by_concept.get(it["concept_code"], 0) + 1
                if it["truth_status"] == "verified":
                    demand_verified_by_concept[it["concept_code"]] = demand_verified_by_concept.get(it["concept_code"], 0) + 1
            elif it["kind"] == "connection":
                conn_by_status[it.get("connection_status", "unknown")] = conn_by_status.get(it.get("connection_status", "unknown"), 0) + 1
                if it.get("connection_status") == "completed":
                    completed_count += 1
                bc = conn_by_concept.setdefault(it["concept_code"], {})
                bc[it.get("connection_status", "unknown")] = bc.get(it.get("connection_status", "unknown"), 0) + 1
                connection_id_list.append({
                    "id": it["id"], "entity_id": it["entity_id"], "concept_code": it["concept_code"],
                    "status": it.get("connection_status", "unknown"),
                })
            elif it["kind"] == "outcome_claim":
                outcome_by_truth[it["truth_status"]] = outcome_by_truth.get(it["truth_status"], 0) + 1
                outcome_id_list.append({
                    "id": it["id"], "entity_id": it["entity_id"], "concept_code": it["concept_code"],
                    "truth_status": it["truth_status"],
                })

        role_dist = {}
        for _, code in role_pairs:
            role_dist[code] = role_dist.get(code, 0) + 1
        supply_by_concept = {}
        for _, code in supply_pairs:
            supply_by_concept[code] = supply_by_concept.get(code, 0) + 1

        binding_denominator = binding_total or None
        verified_outcomes = outcome_by_truth.get("verified", 0)
        pending_outcomes = max(0, completed_count - verified_outcomes)

        excluded_reasons = {}
        for e in excluded:
            reason = e.get("reason", "unknown")
            excluded_reasons[reason] = excluded_reasons.get(reason, 0) + 1

        return {
            "nodes": {
                "unique_count": len(nodes),
                "role_distribution": role_dist,
                "ids": node_ids,
                "role_bindings": role_binding_list,
            },
            "capability_supply": {
                "unique_pairs": len(supply_pairs),
                "unique_nodes": len(supply_nodes),
                "by_concept": supply_by_concept,
                "pairs": supply_pair_list,
            },
            "demand": {
                "unique_events": len(demand_ids),
                "by_concept": demand_by_concept,
                "verified_by_concept": demand_verified_by_concept,
                "verified_count": sum(demand_verified_by_concept.values()),
                "ids": demand_id_list,
            },
            "evidence_claim": {
                "verified_evidence_ids": len(verified_evidence_ids),
                "verified_claim_ids": len(claim_ids),
                "binding_denominator": binding_denominator,
                "binding_coverage": round(len(claim_ids) / binding_total, 4) if binding_total else None,
                "evidence_ids": evidence_id_list,
                "claim_ids": claim_id_list,
            },
            "connection": {
                "status": conn_by_status,
                "by_concept": conn_by_concept,
                "completed_count": completed_count,
                "ids": connection_id_list,
            },
            "outcome": {
                "pending_count": pending_outcomes,
                "claimed_count": outcome_by_truth.get("observed", 0),
                "verified_count": verified_outcomes,
                "ids": outcome_id_list,
            },
            "unknown": {
                "missing_concepts": len(unknown.get("missing_required_concepts") or []),
                "unmapped_companies": len(unknown.get("unmapped_companies") or []),
            },
            "excluded_reasons": excluded_reasons,
        }

    def _gaps(self, items: List[Dict], excluded: List[Dict],
               unknown: Dict, state_scope: str) -> List[Dict]:
        rules = self.config.get("gap_rules", {})
        concepts = set()
        demand_verified = set()
        supply_verified = set()
        supply_observed = set()
        connections_by_concept = {}
        completed_concepts = set()
        outcome_verified_concepts = set()

        for e in excluded:
            if e.get("kind") == "node_binding" and e.get("truth_status") == "observed":
                supply_observed.add(e.get("concept_code"))
        for it in items:
            code = it["concept_code"]
            concepts.add(code)
            if it["kind"] == "demand_binding" and it["truth_status"] == "verified":
                demand_verified.add(code)
            elif it["kind"] == "node_binding":
                if it["truth_status"] == "verified" and it.get("claim_supported"):
                    supply_verified.add(code)
                elif it["truth_status"] == "observed":
                    supply_observed.add(code)
            elif it["kind"] == "connection":
                connections_by_concept.setdefault(code, []).append(it)
                if it.get("connection_status") == "completed":
                    completed_concepts.add(code)
            elif it["kind"] == "outcome_claim" and it["truth_status"] == "verified":
                outcome_verified_concepts.add(code)

        gaps = []
        for code in sorted(concepts):
            conns = connections_by_concept.get(code, [])
            eligible = any(
                c["truth_status"] == "verified" and c.get("decision_scope") == "production"
                and c.get("excluded") is False
                for c in conns
            )
            source_ids = []
            for it in items:
                if it["concept_code"] == code:
                    source_ids.extend(it.get("source_fact_ids") or [])
            source_ids = sorted(set(source_ids))[:20]

            if code in demand_verified and code not in supply_verified:
                gaps.append({"gap_type": "capability_gap", "concept_code": code,
                             "source_fact_ids": source_ids,
                             "calculation_rule": rules.get("capability_gap"),
                             "excluded_reasons": [], "state_scope": state_scope})
            if code in supply_observed and code not in supply_verified:
                gaps.append({"gap_type": "trust_gap", "concept_code": code,
                             "source_fact_ids": source_ids,
                             "calculation_rule": rules.get("trust_gap"),
                             "excluded_reasons": [], "state_scope": state_scope})
            if code in demand_verified and code in supply_verified and not eligible:
                gaps.append({"gap_type": "connection_gap", "concept_code": code,
                             "source_fact_ids": source_ids,
                             "calculation_rule": rules.get("connection_gap"),
                             "excluded_reasons": [], "state_scope": state_scope})
            if code in completed_concepts and code not in outcome_verified_concepts:
                gaps.append({"gap_type": "outcome_gap", "concept_code": code,
                             "source_fact_ids": source_ids,
                             "calculation_rule": rules.get("outcome_gap"),
                             "excluded_reasons": [], "state_scope": state_scope})

        if unknown.get("unmapped_companies") or unknown.get("missing_required_concepts"):
            gaps.append({
                "gap_type": "semantic_gap", "concept_code": None,
                "source_fact_ids": (unknown.get("unmapped_companies") or [])[:10],
                "calculation_rule": rules.get("semantic_gap"),
                "excluded_reasons": [], "state_scope": state_scope,
            })
        return gaps

    async def _get_snapshot(self, db, snapshot_id: str) -> WorldStateSnapshot:
        snap = (await db.execute(select(WorldStateSnapshot).where(
            WorldStateSnapshot.snapshot_id == snapshot_id
        ))).scalars().first()
        if not snap:
            raise ValueError("snapshot not found")
        return snap

    def _to_dict(self, s: WorldStateSnapshot) -> Dict:
        return {
            "snapshot_id": s.snapshot_id,
            "world_code": s.world_code,
            "world_version": s.world_version,
            "config_hash": s.config_hash,
            "state_scope": s.state_scope,
            "projection_as_of": s.projection_as_of,
            "projection_manifest_hash": s.projection_manifest_hash,
            "aggregation_rule_version": s.aggregation_rule_version,
            "aggregation_config_hash": s.aggregation_config_hash,
            "source_manifest_hash": s.source_manifest_hash,
            "dimensions": s.dimensions,
            "truth_distribution": s.truth_distribution,
            "gaps": s.gaps,
            "unknown": s.unknown,
            "excluded": s.excluded,
            "snapshot_hash": s.snapshot_hash,
            "is_stale": s.is_stale,
            "generated_at": s.generated_at.isoformat() if s.generated_at else None,
        }


def get_world_state_service() -> WorldStateService:
    return WorldStateService()
