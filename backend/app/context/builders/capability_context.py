from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.context.retrieval.entity_retriever import EntityRetriever
from app.context.retrieval.relationship_retriever import RelationshipRetriever
from app.context.retrieval.evidence_retriever import EvidenceRetriever
from app.context.schemas.context_schema import (
    CapabilityContext, CapabilityProfile, CompanyBrief,
    IndustryBrief, RelationshipInfo, EvidenceInfo
)
from app.models.company import Company


class CapabilityContextBuilder:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.entity = EntityRetriever(db)
        self.relations = RelationshipRetriever(db)
        self.evidence = EvidenceRetriever(db)

    async def build(self, capability_id: str) -> CapabilityContext:
        cap = await self.entity.get_capability(capability_id)
        if not cap:
            return CapabilityContext(capability=CapabilityProfile(
                id=capability_id, name="", level=0, company_id=capability_id
            ))

        profile = CapabilityProfile(
            id=cap.id, name=cap.name, level=cap.level,
            description=cap.description, category=cap.category,
            company_id=cap.company_id,
        )

        # Provider company
        providers = []
        if cap.company_id:
            provider = await self.entity.get_company(str(cap.company_id))
            if provider:
                providers.append(CompanyBrief(
                    id=provider.id, name=provider.name,
                    geo_score=provider.geo_score or 0, is_verified=provider.is_verified,
                ))

        # Relationships for the provider
        relationships = []
        if cap.company_id:
            rels = await self.relations.get_relationships(str(cap.company_id))
            for r in rels:
                other_id = str(r.target_id) if str(r.source_id) == str(cap.company_id) else str(r.source_id)
                other_name = await self.relations.get_entity_name(other_id)
                relationships.append(RelationshipInfo(
                    id=r.id, source_id=r.source_id, target_id=r.target_id,
                    relation_type=r.relation_type, weight=r.weight,
                    description=r.description, target_name=other_name,
                ))

        # Evidence
        ev_list = await self.evidence.get_evidence(str(cap.company_id)) if cap.company_id else []
        evidence = [
            EvidenceInfo(id=e.id, claim=e.claim, source_url=e.source_url,
                         confidence_level=e.confidence_level, source_type=e.source_type,
                         verified_at=e.verified_at)
            for e in ev_list
        ]

        return CapabilityContext(
            capability=profile, providers=providers,
            industries=[], relationships=relationships, evidence=evidence,
        )
