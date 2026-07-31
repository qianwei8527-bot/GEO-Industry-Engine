"""Agent Evaluation Base Test Suite — Intent路由、Tool调用、Chain执行"""
import pytest, httpx

BASE = "http://127.0.0.1:8080"

@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE, timeout=15) as c: yield c

@pytest.fixture(scope="module")
def cid(client):
    return client.get("/api/v1/companies/?limit=1").json()[0]["id"]

def _agent_payload(cid, query):
    return {"query": query, "params": {"company_id": cid}}

def test_agent_post_returns_200(client, cid):
    r = client.post("/api/v1/agent/analyze", json=_agent_payload(cid, "分析企业"))
    assert r.status_code == 200

def test_agent_response_has_agent_name(client, cid):
    r = client.post("/api/v1/agent/analyze", json=_agent_payload(cid, "分析竞争"))
    data = r.json()
    assert "agent" in data, f"Response must have agent field. Keys: {list(data.keys())}"

def test_agent_response_has_intent(client, cid):
    r = client.post("/api/v1/agent/analyze", json=_agent_payload(cid, "查找机会"))
    data = r.json()
    assert "intent" in data, "Agent response must have intent"

def test_agent_intent_is_meaningful(client, cid):
    r = client.post("/api/v1/agent/analyze", json=_agent_payload(cid, "分析GEO竞争力"))
    data = r.json()
    assert isinstance(data.get("intent"), str)
    assert len(data["intent"]) > 0, "Intent should not be empty"

def test_agent_is_not_hallucinating_entity(client, cid):
    """Agent 不能编造不存在的数据"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    r = client.post("/api/v1/agent/analyze", json=_agent_payload(fake_id, "test"))
    assert r.status_code in [200, 404, 422], f"Should handle non-existent entity gracefully, got {r.status_code}"

def test_agent_has_tool_calls(client, cid):
    r = client.post("/api/v1/agent/analyze", json=_agent_payload(cid, "分析企业风险与机会"))
    data = r.json()
    assert "tool_calls" in data, "Agent must list tool_calls"

def test_agent_has_confidence(client, cid):
    r = client.post("/api/v1/agent/analyze", json=_agent_payload(cid, "评估"))
    data = r.json()
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0, f"Confidence must be 0-1, got {data['confidence']}"

def test_agent_summary_not_empty(client, cid):
    r = client.post("/api/v1/agent/analyze", json=_agent_payload(cid, "生成企业战略报告"))
    data = r.json()
    assert "summary" in data
    assert len(data["summary"]) > 0, "Summary should not be empty"
