"""C8.1-R EvidenceClaim service.

Evidence Authenticity != Claim Support.
A claim is created as observed and only becomes verified through explicit review.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select

from app.models.evidence_claim import EvidenceClaim
from app.models.evidence import Evidence


def _claim_hash(payload: Dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class EvidenceClaimService:
    async def create_claim(self, db, evidence_id: str, subject_type: str, subject_id: str,
                           predicate_code: str, object_type: str, object_code: str,
                           object_value: str = None, claim_text: str = None,
                           source_locator: str = None, extraction_method: str = "structured",
                           valid_from: str = None, valid_until: str = None,
                           metadata: Dict = None) -> Dict:
        try:
            ev = await db.get(Evidence, uuid.UUID(str(evidence_id)))
        except (ValueError, TypeError):
            raise ValueError("evidence_id must be a valid UUID")
        if not ev:
            raise ValueError("evidence not found")
        if not subject_id or not predicate_code or not object_code:
            raise ValueError("subject_id, predicate_code, object_code are required")

        text = claim_text or f"{subject_type}:{subject_id} {predicate_code} {object_code}"
        payload = {
            "evidence_id": str(ev.id),
            "subject_type": subject_type,
            "subject_id": subject_id,
            "predicate_code": predicate_code,
            "object_type": object_type,
            "object_code": object_code,
            "object_value": object_value,
        }
        chash = _claim_hash(payload)
        existing = (await db.execute(select(EvidenceClaim).where(
            EvidenceClaim.claim_hash == chash,
            EvidenceClaim.evidence_id == ev.id,
        ))).scalars().first()
        if existing:
            return self._to_dict(existing)

        claim = EvidenceClaim(
            evidence_id=ev.id,
            subject_type=subject_type,
            subject_id=subject_id,
            predicate_code=predicate_code,
            object_type=object_type,
            object_code=object_code,
            object_value=object_value,
            claim_text=text,
            source_locator=source_locator,
            extraction_method=extraction_method,
            truth_status="observed",
            valid_from=self._parse_dt(valid_from),
            valid_until=self._parse_dt(valid_until),
            may_affect_real_metrics=ev.may_affect_real_metrics,
            claim_hash=chash,
            metadata_json=metadata,
        )
        db.add(claim)
        await db.commit()
        await db.refresh(claim)
        return self._to_dict(claim)

    async def verify_claim(self, db, claim_id: str, verifier_id: str,
                           method: str = "structured_review", result: str = "approved") -> Dict:
        try:
            claim = await db.get(EvidenceClaim, uuid.UUID(str(claim_id)))
        except (ValueError, TypeError):
            raise ValueError("claim_id must be a valid UUID")
        if not claim:
            raise ValueError("claim not found")
        if not verifier_id:
            raise ValueError("verifier_id is required")
        claim.truth_status = "verified"
        claim.verification_method = method
        claim.verification_result = result
        claim.verified_by = str(verifier_id)
        claim.verified_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(claim)
        return self._to_dict(claim)

    async def list_for_evidence(self, db, evidence_id: str) -> List[Dict]:
        rows = (await db.execute(select(EvidenceClaim).where(
            EvidenceClaim.evidence_id == uuid.UUID(str(evidence_id))
        ).order_by(EvidenceClaim.created_at))).scalars().all()
        return [self._to_dict(r) for r in rows]

    async def list_review(self, db, status: str = "observed", limit: int = 100) -> List[Dict]:
        rows = (await db.execute(
            select(EvidenceClaim).where(EvidenceClaim.truth_status == status)
            .order_by(EvidenceClaim.created_at.desc()).limit(limit)
        )).scalars().all()
        return [self._to_dict(r) for r in rows]

    async def audit_legacy_bindings(self, db, world_code: str = None) -> Dict:
        """Downgrade verified bindings that have no structured claim support."""
        from app.models.world_model_contract import WorldBinding, WorldBindingEvidence, VerticalWorld, VerticalWorldVersion
        downgraded = 0
        kept = 0
        q = (select(WorldBinding, VerticalWorld.code, VerticalWorldVersion.version)
             .join(VerticalWorld, VerticalWorld.id == WorldBinding.world_id)
             .join(VerticalWorldVersion, VerticalWorldVersion.id == WorldBinding.version_id)
             .where(WorldBinding.truth_status == "verified"))
        if world_code:
            q = q.where(VerticalWorld.code == world_code)
        rows = (await db.execute(q)).all()
        for binding, code, version in rows:
            links = (await db.execute(select(WorldBindingEvidence).where(
                WorldBindingEvidence.binding_id == binding.id,
                WorldBindingEvidence.evidence_claim_id.isnot(None),
            ))).scalars().all()
            if links:
                kept += 1
            else:
                binding.truth_status = "observed"
                downgraded += 1
        await db.commit()
        return {"downgraded": downgraded, "kept": kept}

    def _to_dict(self, c: EvidenceClaim) -> Dict:
        return {
            "id": str(c.id),
            "evidence_id": str(c.evidence_id),
            "subject_type": c.subject_type,
            "subject_id": c.subject_id,
            "predicate_code": c.predicate_code,
            "object_type": c.object_type,
            "object_code": c.object_code,
            "object_value": c.object_value,
            "claim_text": c.claim_text,
            "source_locator": c.source_locator,
            "extraction_method": c.extraction_method,
            "truth_status": c.truth_status,
            "verification_method": c.verification_method,
            "verification_result": c.verification_result,
            "verified_by": c.verified_by,
            "verified_at": c.verified_at.isoformat() if c.verified_at else None,
            "valid_from": c.valid_from.isoformat() if c.valid_from else None,
            "valid_until": c.valid_until.isoformat() if c.valid_until else None,
            "may_affect_real_metrics": c.may_affect_real_metrics,
            "claim_hash": c.claim_hash,
        }

    @staticmethod
    def _parse_dt(value):
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None


def get_evidence_claim_service() -> EvidenceClaimService:
    return EvidenceClaimService()
