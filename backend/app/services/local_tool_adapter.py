"""V10-P0-R local real tool adapter.

This adapter runs local, deterministic tools against granted Realm facts.
It never claims to be an external AI provider and never fabricates verified
results. Output is always observed.
"""

from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evidence import Evidence
from app.models.evidence_claim import EvidenceClaim


async def run_local_tool(db: AsyncSession, tool_name: str, input_manifest: Dict,
                         realm_entity_id: str) -> Dict:
    if tool_name == "geo_visibility":
        return await _geo_visibility(db, input_manifest, realm_entity_id)
    if tool_name == "geo_diagnosis":
        return await _geo_diagnosis(db, input_manifest, realm_entity_id)
    if tool_name == "geo_report":
        return await _geo_report(db, input_manifest, realm_entity_id)
    raise ValueError(f"unknown local tool: {tool_name}")


async def _geo_visibility(db: AsyncSession, input_manifest: Dict, realm_entity_id: str) -> Dict:
    target = (input_manifest or {}).get("target_brand") or ""
    question_set = (input_manifest or {}).get("question_set") or []
    evidence_rows = (await db.execute(
        select(Evidence).where(Evidence.entity_id == realm_entity_id)
    )).scalars().all()
    claims = (await db.execute(
        select(EvidenceClaim).where(EvidenceClaim.subject_id == str(realm_entity_id))
    )).scalars().all()
    mentioned = 0
    cited = 0
    for ev in evidence_rows:
        text = f"{ev.claim or ''} {ev.excerpt or ''}"
        if target and target in text:
            mentioned += 1
        if ev.truth_status == "verified":
            cited += 1
    for c in claims:
        if target and target in (c.claim_text or ""):
            mentioned += 1
    sample = max(len(question_set), 1)
    output = {
        "tool": "geo_visibility",
        "execution_source": "system",
        "provider": "universe",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "target_brand": target,
        "question_count": len(question_set),
        "mention_count": mentioned,
        "citation_count": cited,
        "mention_rate": round(mentioned / sample, 4),
        "citation_rate": round(cited / sample, 4),
        "based_on_real_data": len(evidence_rows) > 0,
        "truth_status": "observed",
        "data_origin": "local_real",
    }
    return {
        "status": "success",
        "output_manifest": output,
        "source_fact_ids": [str(e.id) for e in evidence_rows],
        "truth_status": "observed",
        "cost": 0.0,
        "completed_at": datetime.now(timezone.utc),
    }


async def _geo_diagnosis(db: AsyncSession, input_manifest: Dict, realm_entity_id: str) -> Dict:
    target = (input_manifest or {}).get("target_brand") or ""
    evidence_rows = (await db.execute(
        select(Evidence).where(Evidence.entity_id == realm_entity_id)
    )).scalars().all()
    claims = (await db.execute(
        select(EvidenceClaim).where(EvidenceClaim.subject_id == str(realm_entity_id))
    )).scalars().all()
    verified_claims = [c for c in claims if c.truth_status == "verified"]
    output = {
        "tool": "geo_diagnosis",
        "target_brand": target,
        "fact_count": len(evidence_rows),
        "verified_claim_count": len(verified_claims),
        "gaps": {
            "facts": len(evidence_rows) < 3,
            "structured_claims": len(verified_claims) < 1,
            "citations": sum(1 for e in evidence_rows if e.truth_status == "verified") < 1,
            "channels": True,
        },
        "based_on_real_data": len(evidence_rows) > 0,
        "truth_status": "observed",
        "data_origin": "local_real",
    }
    return {
        "status": "success",
        "output_manifest": output,
        "source_fact_ids": [str(e.id) for e in evidence_rows],
        "truth_status": "observed",
        "cost": 0.0,
        "completed_at": datetime.now(timezone.utc),
    }


async def _geo_report(db: AsyncSession, input_manifest: Dict, realm_entity_id: str) -> Dict:
    observation = await _geo_visibility(db, input_manifest, realm_entity_id)
    diagnosis = await _geo_diagnosis(db, input_manifest, realm_entity_id)
    output = {
        "tool": "geo_report",
        "title": "GEO 观察与诊断报告",
        "observation": observation["output_manifest"],
        "diagnosis": diagnosis["output_manifest"],
        "truth_status": "observed",
        "data_origin": "local_real",
    }
    return {
        "status": "success",
        "output_manifest": output,
        "source_fact_ids": observation.get("source_fact_ids") or [],
        "truth_status": "observed",
        "cost": 0.0,
        "completed_at": datetime.now(timezone.utc),
    }
