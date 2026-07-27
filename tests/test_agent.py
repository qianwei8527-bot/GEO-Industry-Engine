import pytest
from agents.router.intent_router import IntentRouter


class TestIntentRouter:
    def test_route_industry(self):
        name = IntentRouter.route("analisi del settore AI")
        assert name is not None

    def test_route_company(self):
        name = IntentRouter.route("azienda di marketing AI")
        assert name is not None

    def test_route_growth(self):
        name = IntentRouter.route("geo visibility score")
        assert name is not None

    def test_route_default(self):
        name = IntentRouter.route("generic query about data")
        assert name in ["analyst_agent", "industry_agent", "company_agent", "geo_growth_agent"]

    def test_route_chinese_industry(self):
        name = IntentRouter.route("分析医疗AI行业趋势")
        assert name == "industry_agent"

    def test_route_chinese_company(self):
        name = IntentRouter.route("查看企业AI能力")
        assert name == "company_agent"
