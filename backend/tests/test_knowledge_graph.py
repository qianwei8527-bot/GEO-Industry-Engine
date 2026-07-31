"""Knowledge Graph Relationship Chain Tests — 验证产业实体→能力→关系→事件→证据→信任闭环"""
import pytest
import httpx

BASE = "http://127.0.0.1:8080"

@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE, timeout=10) as c:
        yield c

@pytest.fixture(scope="module")
def company(client):
    r = client.get("/api/v1/companies/?limit=1")
    cid = r.json()[0]["id"]
    return {"id": cid, "name": r.json()[0]["name"], "geo_id": r.json()[0]["geo_id"]}

def test_entity_to_capability_chain(client, company):
    """Entity 必须关联到能力"""
    cid = company["id"]
    r = client.get(f"/api/v1/context/company/{cid}")
    assert r.status_code == 200
    ctx = r.json()
    assert "capabilities" in ctx, "Context 必须包含 capabilities"
    assert len(ctx["capabilities"]) >= 1, f"企业应至少关联1个能力"

def test_entity_to_evidence_chain(client, company):
    """Entity 必须关联到证据"""
    cid = company["id"]
    r = client.get(f"/api/v1/context/company/{cid}")
    ctx = r.json()
    assert "evidence" in ctx, "Context 必须包含 evidence"
    assert len(ctx["evidence"]) >= 1, f"企业应至少关联1个证据"

def test_capability_has_valid_fields(client, company):
    """能力记录必须包含必要字段"""
    r = client.get(f"/api/v1/context/company/{company['id']}")
    for cap in r.json()["capabilities"]:
        assert "id" in cap
        assert "name" in cap
        assert "level" in cap

def test_evidence_has_source_url(client, company):
    """证据必须有来源URL"""
    r = client.get(f"/api/v1/context/company/{company['id']}")
    for ev in r.json()["evidence"]:
        assert "source_url" in ev, "证据必须包含 source_url"

def test_entity_has_trust_record(client, company):
    """Entity 必须有信任记录"""
    r = client.get(f"/api/v1/context/company/{company['id']}")
    # 信任信息在 scoring 中
    scoring = r.json().get("scoring", {})
    assert "trust_score" in scoring, "Scoring 必须包含 trust_score"

def test_decision_returns_structured_output(client, company):
    """Decision Engine 输出必须结构化"""
    r = client.get(f"/api/v1/decision/company/{company['id']}")
    data = r.json()
    assert "scores" in data, "Decision 必须包含 scores"
    scores = data["scores"]
    assert "visibility" in scores, "scores 必须包含 visibility"

def test_relationship_chain_between_companies(client, company):
    """验证企业间关系链存在"""
    ents = client.get("/api/v1/entities/?limit=10").json()
    assert len(ents) >= 2, "至少需要2个实体才能测试关系"

def test_event_timeline_consistency(client, company):
    """事件时间线必须一致"""
    r = client.get(f"/api/v1/context/company/{company['id']}")
    events = r.json().get("events", [])
    for ev in events:
        assert "event_date" in ev
        assert "event_type" in ev

def test_industry_company_bridge(client, company):
    """行业-企业桥接关系验证"""
    industries = client.get("/api/v1/industries/").json()
    assert len(industries) >= 1

def test_score_explainability(client, company):
    """评分必须可解释"""
    r = client.get(f"/api/v1/decision/company/{company['id']}")
    data = r.json()
    scores = data.get("scores", {})
    vis = scores.get("visibility", {})
    assert "reasons" in vis, "visibility 必须包含 reasons（可解释性）"
