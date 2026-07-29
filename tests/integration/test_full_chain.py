# GEO-Industry-Engine 全链路集成测试
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.agents import registry
from app.agents.router.intent_router import intent_router

@pytest.mark.anyio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data

@pytest.mark.anyio
async def test_core_apis_accessible():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        endpoints = [
            ("GET", "/api/v1/companies/"),
            ("GET", "/api/v1/industries/"),
            ("GET", "/api/v1/entities/"),
            ("GET", "/api/v1/relationships/"),
            ("GET", "/api/v1/evidence/"),
            ("GET", "/api/v1/admin/configs"),
            ("GET", "/api/v1/admin/stats"),
            ("GET", "/api/v1/intelligence/competitors"),
            ("GET", "/api/v1/marketplace/demands"),
        ]
        for method, path in endpoints:
            resp = await client.get(path)
            assert resp.status_code != 404, f"路由未注册: {path}"
            assert resp.status_code != 500, f"服务端错误: {path}"

@pytest.mark.anyio
async def test_context_engine_structure():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/context/query", json={"query": "腾讯", "limit": 5})
        assert resp.status_code != 404, "Context query 路由未注册"

@pytest.mark.anyio
async def test_decision_engine_structure():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/decision/company/test-id")
        assert resp.status_code != 404, "Decision company 路由未注册"

@pytest.mark.anyio
async def test_agent_registry_has_four_agents():
    agents = registry.list_all()
    assert len(agents) >= 4, f"Agent 数量不足: {len(agents)}"
    required = ["IndustryAnalyst", "CompanyIntelligence", "GEOGrowth", "DataAnalyst"]
    for name in required:
        assert name in agents, f"缺失 Agent: {name}"

@pytest.mark.anyio
async def test_agent_instantiation():
    from app.agents.core.base_agent import BaseAgent
    for name in ["IndustryAnalyst", "CompanyIntelligence", "GEOGrowth", "DataAnalyst"]:
        agent = registry.get(name)
        assert agent is not None, f"Agent {name} 未注册"
        assert isinstance(agent, BaseAgent), f"Agent {name} 未继承 BaseAgent"
        assert hasattr(agent, "execute"), f"Agent {name} 缺少 execute 方法"
        assert hasattr(agent, "use_tool"), f"Agent {name} 缺少 use_tool 方法"

@pytest.mark.anyio
async def test_intent_router_accuracy():
    test_cases = [
        ("企业", "company"),
        ("分析腾讯", "analyze"),
        ("行业趋势", "industry"),
        ("GEO优化", "geo_growth"),
        ("提升可见度", "geo_growth"),
        ("检测报告", "analyze"),
        ("评估分析", "analyze"),
        ("杭州AI营销", "analyze"),
    ]
    for query, expected in test_cases:
        intent, confidence = intent_router.route(query)
        assert intent == expected, f"query={query} 期望 intent={expected} 但得到 {intent}"

@pytest.mark.anyio
async def test_agent_execution_returns_result():
    from app.agents.core.base_agent import AgentContext
    agent = registry.get("IndustryAnalyst")
    ctx = AgentContext(intent="industry", input_query="测试行业分析", params={"industry_id": "test"})
    result = await agent.execute(ctx)
    assert result is not None, "Agent 返回 None"
    assert hasattr(result, "success"), "AgentResult 缺少 success"
    assert hasattr(result, "summary"), "AgentResult 缺少 summary"
    assert isinstance(result.success, bool), "success 应为 bool"

@pytest.mark.anyio
async def test_agent_api_contract():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/agent/list")
        assert resp.status_code == 200
        data = resp.json()
        assert "agents" in data
        assert len(data["agents"]) >= 4

@pytest.mark.anyio
async def test_context_query_contract():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/context/query", json={"query": "测试查询", "limit": 5})
        assert resp.status_code != 422, "请求参数格式错误"
        assert resp.status_code != 404, "路由未注册"

@pytest.mark.anyio
async def test_decision_analyze_contract():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/decision/analyze", json={"query": "分析行业"})
        assert resp.status_code != 422, "请求参数格式错误"
        assert resp.status_code != 404, "路由未注册"

@pytest.mark.anyio
async def test_analytics_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/analytics/events/batch", json={"events": [
            {"event_type": "page_view", "session_id": "test", "source": "web", "properties": {}}
        ]})
        assert resp.status_code != 404, "Analytics 路由未注册"

@pytest.mark.anyio
async def test_certification_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/certification/levels")
        assert resp.status_code != 404, "Certification levels 路由未注册"
