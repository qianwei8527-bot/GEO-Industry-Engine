from sqlalchemy.ext.asyncio import AsyncSession
from app.context.retrieval.entity_retriever import EntityRetriever
from app.context.retrieval.relationship_retriever import RelationshipRetriever
from app.context.retrieval.evidence_retriever import EvidenceRetriever
from app.context.ranking.trust_score import TrustScorer
from app.context.ranking.geo_score import GEOScorer
from app.context.schemas.context_schema import (
    CompanyContext, CompanyProfile, IndustryBrief,
    CapabilityInfo, RelationshipInfo, EventInfo, EvidenceInfo,
    ScoringSummary, OpportunityInfo
)


class CompanyContextBuilder:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.entity = EntityRetriever(db)
        self.relations = RelationshipRetriever(db)
        self.evidence = EvidenceRetriever(db)

    async def build(self, company_id: str) -> CompanyContext:
        company = await self.entity.get_company(company_id)
        if not company:
            return CompanyContext(company=CompanyProfile(id=company_id, name="", entity_type="company"))

        # Company profile
        profile = CompanyProfile(
            id=company.id, geo_id=company.geo_id or "",
            name=company.name, entity_type=company.entity_type or "company",
            description=company.description, website=company.website,
            company_size=company.company_size,
            is_verified=company.is_verified,
            subscription_tier=company.subscription_tier,
        )

        # Capabilities
        caps = await self.entity.get_capabilities_by_company(company_id)
        capabilities = [CapabilityInfo(id=c.id, name=c.name, level=c.level, category=c.category) for c in caps]

        # Relationships
        rels = await self.relations.get_relationships(company_id)
        relationships = []
        for r in rels:
            other_id = str(r.target_id) if str(r.source_id) == company_id else str(r.source_id)
            other_name = await self.relations.get_entity_name(other_id)
            other_type = await self.relations.get_entity_type(other_id)
            relationships.append(RelationshipInfo(
                id=r.id, source_id=r.source_id, target_id=r.target_id,
                relation_type=r.relation_type, weight=r.weight,
                description=r.description,
                target_name=other_name, target_type=other_type,
            ))

        # Events
        from app.models.event import Event
        from sqlalchemy import select
        stmt = select(Event).where(Event.entity_id == company_id).order_by(Event.occurred_at.desc()).limit(20)
        result = await self.db.execute(stmt)
        events = [
            EventInfo(id=e.id, event_type=e.event_type, title=e.title,
                      occurred_at=e.occurred_at, description=e.description,
                      impact_level=e.impact_level)
            for e in result.scalars().all()
        ]

        # Evidence
        ev_list = await self.evidence.get_evidence(company_id)
        evidence = [
            EvidenceInfo(id=e.id, claim=e.claim, source_url=e.source_url,
                         confidence_level=e.confidence_level, source_type=e.source_type,
                         verified_at=e.verified_at)
            for e in ev_list
        ]

        # Scoring
        trust = await TrustScorer(self.db).compute(company_id)
        geo = GEOScorer.compute(company.geo_score)
        scoring = ScoringSummary(
            trust_score=trust["score"],
            geo_score=geo["raw_score"],
            overall=round(trust["score"] * 0.4 + geo["normalized"] * 0.3 + 30, 1),
        )

        return CompanyContext(
            company=profile, industries=[], capabilities=capabilities,
            relationships=relationships, events=events, evidence=evidence,
            scoring=scoring, opportunities=[OpportunityInfo(title="", description="", relevance=0.0)],
        )
