"""C8.3 World State Transition Engine.

Deterministic diff between two compatible World State Snapshots.
Detects changes only; no trends, no causation, no scores.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

import yaml
from sqlalchemy import select

from app.models.world_transition import WorldStateTransition
from app.models.world_state_snapshot import WorldStateSnapshot


def _load_config() -> Dict:
    p = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        'config', 'universe', 'world_transition.yaml',
    )
    raw = open(p, encoding='utf-8').read()
    data = yaml.safe_load(raw) or {}
    data['config_hash'] = hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]
    return data


def _canonical_hash(payload: Dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()[:32]


class WorldTransitionService:
    def __init__(self):
        self.config = _load_config()

    async def generate(self, db, from_snapshot_id: str, to_snapshot_id: str) -> Dict:
        from_snap = await self._get_snapshot(db, from_snapshot_id)
        to_snap = await self._get_snapshot(db, to_snapshot_id)
        compatibility, reason = self._compatibility(from_snap, to_snap)

        change_manifest = []
        gap_lifecycle = []
        if compatibility == "comparable":
            change_manifest = self._diff(from_snap, to_snap)
            gap_lifecycle = self._gap_lifecycle(from_snap, to_snap)

        drift = bool(from_snap.is_stale or to_snap.is_stale)
        fully_auditable = compatibility == "comparable" and not drift
        payload = {
            "from_snapshot_id": str(from_snap.id),
            "to_snapshot_id": str(to_snap.id),
            "from_hash": from_snap.snapshot_hash,
            "to_hash": to_snap.snapshot_hash,
            "compatibility": compatibility,
            "rule_version": self.config.get("version"),
            "config_hash": self.config.get("config_hash"),
            "change_manifest": change_manifest,
            "gap_lifecycle": gap_lifecycle,
            "drift": drift,
            "fully_auditable": fully_auditable,
        }
        transition_hash = _canonical_hash(payload)

        existing = (await db.execute(select(WorldStateTransition).where(
            WorldStateTransition.transition_hash == transition_hash
        ))).scalars().first()
        if existing:
            return self._to_dict(existing)

        transition = WorldStateTransition(
            transition_id=str(uuid.uuid4()),
            from_snapshot_id=from_snap.id,
            to_snapshot_id=to_snap.id,
            world_code=from_snap.world_code,
            world_version=from_snap.world_version,
            state_scope=from_snap.state_scope,
            compatibility_result=compatibility,
            non_comparable_reason=reason or None,
            from_snapshot_hash=from_snap.snapshot_hash,
            to_snapshot_hash=to_snap.snapshot_hash,
            transition_rule_version=self.config.get("version", "1.0.0"),
            transition_config_hash=self.config.get("config_hash"),
            change_manifest=change_manifest,
            gap_lifecycle=gap_lifecycle,
            truth_scope_info={"scope": from_snap.state_scope, "world_version": from_snap.world_version},
            transition_hash=transition_hash,
            historical_source_drift=drift,
            fully_auditable=fully_auditable,
            generated_at=datetime.now(timezone.utc),
        )
        db.add(transition)
        await db.commit()
        await db.refresh(transition)
        return self._to_dict(transition)

    async def get(self, db, transition_id: str) -> Dict:
        t = await self._get_transition(db, transition_id)
        return self._to_dict(t)

    async def list_transitions(self, db, limit: int = 50) -> List[Dict]:
        rows = (await db.execute(
            select(WorldStateTransition).order_by(WorldStateTransition.created_at.desc()).limit(limit)
        )).scalars().all()
        return [self._to_dict(r) for r in rows]

    async def compatibility(self, db, from_snapshot_id: str, to_snapshot_id: str) -> Dict:
        from_snap = await self._get_snapshot(db, from_snapshot_id)
        to_snap = await self._get_snapshot(db, to_snapshot_id)
        result, reason = self._compatibility(from_snap, to_snap)
        return {"compatibility_result": result, "reasons": reason or []}

    async def changes(self, db, transition_id: str, change_type: str = None,
                      concept_code: str = None) -> List[Dict]:
        t = await self._get_transition(db, transition_id)
        changes = t.change_manifest or []
        if change_type:
            changes = [c for c in changes if c.get("change_type") == change_type]
        if concept_code:
            changes = [c for c in changes if c.get("concept_code") == concept_code]
        return changes

    async def gap_lifecycle(self, db, transition_id: str) -> List[Dict]:
        t = await self._get_transition(db, transition_id)
        return t.gap_lifecycle or []

    async def source_chain(self, db, transition_id: str) -> Dict:
        t = await self._get_transition(db, transition_id)
        source_ids = []
        for c in (t.change_manifest or []):
            source_ids.extend(c.get("added_source_fact_ids") or [])
            source_ids.extend(c.get("removed_source_fact_ids") or [])
        return {
            "transition_id": t.transition_id,
            "from_snapshot_id": str(t.from_snapshot_id),
            "to_snapshot_id": str(t.to_snapshot_id),
            "from_snapshot_hash": t.from_snapshot_hash,
            "to_snapshot_hash": t.to_snapshot_hash,
            "source_fact_ids": sorted(set(source_ids)),
        }

    async def integrity(self, db, transition_id: str) -> Dict:
        t = await self._get_transition(db, transition_id)
        from_snap = await db.get(WorldStateSnapshot, t.from_snapshot_id)
        to_snap = await db.get(WorldStateSnapshot, t.to_snapshot_id)
        return {
            "transition_id": t.transition_id,
            "compatibility_result": t.compatibility_result,
            "historical_source_drift": t.historical_source_drift,
            "fully_auditable": t.fully_auditable,
            "from_snapshot_stale": from_snap.is_stale,
            "to_snapshot_stale": to_snap.is_stale,
            "from_snapshot_hash_ok": from_snap.snapshot_hash == t.from_snapshot_hash,
            "to_snapshot_hash_ok": to_snap.snapshot_hash == t.to_snapshot_hash,
        }

    # ---- compatibility ----

    def _compatibility(self, a: WorldStateSnapshot, b: WorldStateSnapshot):
        reasons = []
        if a.world_code != b.world_code:
            reasons.append("world_code_mismatch")
        if a.world_version != b.world_version:
            reasons.append("world_version_mismatch_is_model_diff")
        if a.state_scope != b.state_scope:
            reasons.append("state_scope_mismatch")
        if a.aggregation_rule_version != b.aggregation_rule_version:
            reasons.append("aggregation_rule_version_mismatch_is_methodology_change")
        if a.aggregation_config_hash != b.aggregation_config_hash:
            reasons.append("aggregation_config_hash_mismatch_is_methodology_change")
        if self._parse_as_of(a.projection_as_of) >= self._parse_as_of(b.projection_as_of):
            reasons.append("from_as_of_not_less_than_to_as_of")
        return ("non_comparable" if reasons else "comparable", reasons)

    @staticmethod
    def _parse_as_of(value: str):
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return datetime.min.replace(tzinfo=timezone.utc)

    # ---- diff ----

    def _diff(self, a: WorldStateSnapshot, b: WorldStateSnapshot) -> List[Dict]:
        ad = a.dimensions or {}
        bd = b.dimensions or {}
        changes: List[Dict] = []

        def add(change_type, dimension_type, concept_code, old_value, new_value,
                delta, added_ids, removed_ids, calc_rule):
            changes.append({
                "change_type": change_type,
                "dimension_type": dimension_type,
                "concept_code": concept_code,
                "old_value": old_value,
                "new_value": new_value,
                "delta": delta,
                "added_source_fact_ids": sorted(added_ids),
                "removed_source_fact_ids": sorted(removed_ids),
                "associated_source_changes": [],
                "state_scope": a.state_scope,
                "calculation_rule": calc_rule,
            })

        rules = self.config.get("calculation_rules", {})
        a_nodes = set((ad.get("nodes") or {}).get("ids", []))
        b_nodes = set((bd.get("nodes") or {}).get("ids", []))
        for nid in sorted(b_nodes - a_nodes):
            add("projection_entity_added", "node", None, None, nid, 1, [nid], [], rules.get("projection_entity_added"))
        for nid in sorted(a_nodes - b_nodes):
            add("projection_entity_removed", "node", None, nid, None, -1, [], [nid], rules.get("projection_entity_removed"))

        a_roles = {(r["entity_id"], r["concept_code"]) for r in (ad.get("nodes") or {}).get("role_bindings", [])}
        b_roles = {(r["entity_id"], r["concept_code"]) for r in (bd.get("nodes") or {}).get("role_bindings", [])}
        for entity, concept in sorted(b_roles - a_roles):
            add("role_binding_added", "role_binding", concept, None, entity, 1, [entity], [], rules.get("role_binding_added"))
        for entity, concept in sorted(a_roles - b_roles):
            add("role_binding_removed", "role_binding", concept, entity, None, -1, [], [entity], rules.get("role_binding_removed"))

        a_supply = {(p["entity_id"], p["concept_code"]) for p in (ad.get("capability_supply") or {}).get("pairs", [])}
        b_supply = {(p["entity_id"], p["concept_code"]) for p in (bd.get("capability_supply") or {}).get("pairs", [])}
        for entity, concept in sorted(b_supply - a_supply):
            add("capability_supply_added", "capability_supply", concept, None, entity, 1, [entity], [], rules.get("capability_supply_added"))
        for entity, concept in sorted(a_supply - b_supply):
            add("capability_supply_removed", "capability_supply", concept, entity, None, -1, [], [entity], rules.get("capability_supply_removed"))

        a_demands = set((ad.get("demand") or {}).get("ids", []))
        b_demands = set((bd.get("demand") or {}).get("ids", []))
        for did in sorted(b_demands - a_demands):
            add("demand_added", "demand", None, None, did, 1, [did], [], rules.get("demand_added"))
        for did in sorted(a_demands - b_demands):
            add("demand_closed", "demand", None, did, None, -1, [], [did], rules.get("demand_closed"))
        a_verified_demand = (ad.get("demand") or {}).get("verified_count", 0)
        b_verified_demand = (bd.get("demand") or {}).get("verified_count", 0)
        if b_verified_demand != a_verified_demand:
            add("demand_updated", "demand", None, a_verified_demand, b_verified_demand,
                b_verified_demand - a_verified_demand, [], [], rules.get("demand_updated"))

        a_ev = set((ad.get("evidence_claim") or {}).get("evidence_ids", []))
        b_ev = set((bd.get("evidence_claim") or {}).get("evidence_ids", []))
        a_claims = set((ad.get("evidence_claim") or {}).get("claim_ids", []))
        b_claims = set((bd.get("evidence_claim") or {}).get("claim_ids", []))
        if len(b_ev) > len(a_ev) or len(b_claims) > len(a_claims):
            add("evidence_or_claim_verified", "evidence_claim", None, len(a_ev) + len(a_claims),
                len(b_ev) + len(b_claims), len(b_ev) + len(b_claims) - len(a_ev) - len(a_claims),
                sorted(b_ev - a_ev) + sorted(b_claims - a_claims), [], rules.get("evidence_or_claim_verified"))
        if len(b_ev) < len(a_ev) or len(b_claims) < len(a_claims):
            add("evidence_or_claim_revoked_or_expired", "evidence_claim", None, len(a_ev) + len(a_claims),
                len(b_ev) + len(b_claims), len(b_ev) + len(b_claims) - len(a_ev) - len(a_claims),
                [], sorted(a_ev - b_ev) + sorted(a_claims - b_claims), rules.get("evidence_or_claim_revoked_or_expired"))

        a_conn = {c["id"]: c.get("status") for c in (ad.get("connection") or {}).get("ids", [])}
        b_conn = {c["id"]: c.get("status") for c in (bd.get("connection") or {}).get("ids", [])}
        for cid in sorted(set(b_conn) & set(a_conn)):
            if b_conn[cid] != a_conn[cid]:
                add("connection_status_changed", "connection", None, a_conn[cid], b_conn[cid],
                    0, [cid], [], rules.get("connection_status_changed"))
        for cid in sorted(set(b_conn) - set(a_conn)):
            add("connection_status_changed", "connection", None, None, b_conn[cid], 1, [cid], [], rules.get("connection_status_changed"))
        for cid in sorted(set(a_conn) - set(b_conn)):
            add("connection_status_changed", "connection", None, a_conn[cid], None, -1, [], [cid], rules.get("connection_status_changed"))

        a_out = {o["id"]: o.get("truth_status") for o in (ad.get("outcome") or {}).get("ids", [])}
        b_out = {o["id"]: o.get("truth_status") for o in (bd.get("outcome") or {}).get("ids", [])}
        if sum(1 for v in b_out.values() if v == "verified") > sum(1 for v in a_out.values() if v == "verified"):
            add("outcome_verified", "outcome", None, sum(1 for v in a_out.values() if v == "verified"),
                sum(1 for v in b_out.values() if v == "verified"), 1,
                [k for k, v in b_out.items() if v == "verified"], [], rules.get("outcome_verified"))
        if sum(1 for v in b_out.values() if v == "observed") > sum(1 for v in a_out.values() if v == "observed"):
            add("outcome_claimed", "outcome", None, sum(1 for v in a_out.values() if v == "observed"),
                sum(1 for v in b_out.values() if v == "observed"), 1, [], [], rules.get("outcome_claimed"))
        if sum(1 for v in b_out.values() if v == "verified") < sum(1 for v in a_out.values() if v == "verified"):
            add("outcome_revoked", "outcome", None, sum(1 for v in a_out.values() if v == "verified"),
                sum(1 for v in b_out.values() if v == "verified"), -1, [], [], rules.get("outcome_revoked"))

        # fill associated source changes by concept
        by_concept: Dict[str, List[str]] = {}
        for c in changes:
            key = c.get("concept_code") or ""
            by_concept.setdefault(key, []).append(c["change_type"])
        for c in changes:
            key = c.get("concept_code") or ""
            c["associated_source_changes"] = [t for t in by_concept.get(key, []) if t != c["change_type"]]
        return changes

    def _gap_lifecycle(self, a: WorldStateSnapshot, b: WorldStateSnapshot) -> List[Dict]:
        a_keys = {(g["gap_type"], g.get("concept_code")) for g in (a.gaps or [])}
        b_keys = {(g["gap_type"], g.get("concept_code")) for g in (b.gaps or [])}
        out = []
        for key in sorted(a_keys | b_keys, key=lambda x: (x[0], str(x[1]))):
            gap_type, concept = key
            if key in a_keys and key in b_keys:
                out.append({"gap_type": gap_type, "concept_code": concept, "status": "gap_persisted"})
            elif key in b_keys:
                out.append({"gap_type": gap_type, "concept_code": concept, "status": "gap_opened"})
            else:
                out.append({"gap_type": gap_type, "concept_code": concept, "status": "gap_resolved"})
        return out

    async def _get_snapshot(self, db, snapshot_id: str) -> WorldStateSnapshot:
        snap = (await db.execute(select(WorldStateSnapshot).where(
            WorldStateSnapshot.snapshot_id == snapshot_id
        ))).scalars().first()
        if not snap:
            raise ValueError("snapshot not found")
        return snap

    async def _get_transition(self, db, transition_id: str) -> WorldStateTransition:
        t = (await db.execute(select(WorldStateTransition).where(
            WorldStateTransition.transition_id == transition_id
        ))).scalars().first()
        if not t:
            raise ValueError("transition not found")
        return t

    def _to_dict(self, t: WorldStateTransition) -> Dict:
        return {
            "transition_id": t.transition_id,
            "from_snapshot_id": str(t.from_snapshot_id),
            "to_snapshot_id": str(t.to_snapshot_id),
            "world_code": t.world_code,
            "world_version": t.world_version,
            "state_scope": t.state_scope,
            "compatibility_result": t.compatibility_result,
            "non_comparable_reason": t.non_comparable_reason,
            "from_snapshot_hash": t.from_snapshot_hash,
            "to_snapshot_hash": t.to_snapshot_hash,
            "transition_rule_version": t.transition_rule_version,
            "transition_config_hash": t.transition_config_hash,
            "change_manifest": t.change_manifest,
            "gap_lifecycle": t.gap_lifecycle,
            "truth_scope_info": t.truth_scope_info,
            "transition_hash": t.transition_hash,
            "historical_source_drift": t.historical_source_drift,
            "fully_auditable": t.fully_auditable,
            "generated_at": t.generated_at.isoformat() if t.generated_at else None,
        }


def get_world_transition_service() -> WorldTransitionService:
    return WorldTransitionService()
