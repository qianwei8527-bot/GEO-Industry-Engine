import pytest
import uuid
from types import SimpleNamespace
from app.context.ranking.geo_score import GEOScorer
from app.context.ranking.relevance import RelevanceScorer
from app.context.schemas.context_schema import (
    CompanyContext, IndustryContext, CapabilityContext,
    ContextQueryRequest, CompanyProfile, IndustryProfile, CapabilityProfile,
)


class TestContextSchemas:
    def test_company_context_defaults(self):
        p = CompanyProfile(id=uuid.uuid4(), name="T", entity_type="company", geo_id="GEO-TEST")
        ctx = CompanyContext(company=p)
        assert ctx.scoring.trust_score == 0.0
        assert len(ctx.capabilities) == 0

    def test_industry_context_defaults(self):
        p = IndustryProfile(id=uuid.uuid4(), name="AI", code="AI", level=1)
        ctx = IndustryContext(industry=p)
        assert len(ctx.companies) == 0

    def test_capability_context_defaults(self):
        p = CapabilityProfile(id=uuid.uuid4(), name="ML", level=2, company_id=uuid.uuid4())
        ctx = CapabilityContext(capability=p)
        assert len(ctx.providers) == 0

    def test_query_request(self):
        req = ContextQueryRequest(query="AI healthcare")
        assert req.limit == 10


class TestGEOScorer:
    def test_levels(self):
        assert GEOScorer._level(85) == "excellent"
        assert GEOScorer._level(65) == "good"
        assert GEOScorer._level(45) == "average"
        assert GEOScorer._level(15) == "developing"

    def test_compute(self):
        r = GEOScorer.compute(72)
        assert r["raw_score"] == 72
        assert r["level"] == "good"

    def test_none(self):
        r = GEOScorer.compute(None)
        assert r["raw_score"] == 0


class TestRelevanceScorer:
    def test_name_match(self):
        c = SimpleNamespace(name="AI Ltd", description="", website="", geo_score=0, entity_type="company")
        s = RelevanceScorer.score_companies("AI", [c])
        assert s[0][1] > 0

    def test_empty_query(self):
        c = SimpleNamespace(name="Test", description="", website="", geo_score=0, entity_type="company")
        s = RelevanceScorer.score_companies("", [c])
        assert s[0][1] == 0.5

    def test_ordering(self):
        c1 = SimpleNamespace(name="AI Co", description="AI", website="", geo_score=80, entity_type="company")
        c2 = SimpleNamespace(name="Other", description="Other", website="", geo_score=50, entity_type="company")
        s = RelevanceScorer.score_companies("AI", [c1, c2])
        assert s[0][1] >= s[1][1]
