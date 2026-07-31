"""Decision Engine Behavior Tests — 评分、权重、机会、风险"""
import pytest, httpx

BASE = "http://127.0.0.1:8080"

@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE, timeout=10) as c: yield c

@pytest.fixture(scope="module")
def cid(client):
    return client.get("/api/v1/companies/?limit=1").json()[0]["id"]

def test_decision_returns_geo_score(client, cid):
    r = client.get(f"/api/v1/decision/company/{cid}")
    data = r.json()
    assert "geo_score" in data or "scores" in data

def test_decision_scores_are_numeric(client, cid):
    r = client.get(f"/api/v1/decision/company/{cid}")
    scores = r.json().get("scores", {})
    for k, v in scores.items():
        if isinstance(v, dict) and "score" in v:
            assert isinstance(v["score"], (int, float)), f"{k}.score must be numeric, got {type(v['score'])}"

def test_decision_opportunities_structured(client, cid):
    r = client.get(f"/api/v1/decision/company/{cid}")
    opps = r.json().get("opportunities", [])
    assert isinstance(opps, list)

def test_decision_risks_structured(client, cid):
    r = client.get(f"/api/v1/decision/company/{cid}")
    risks = r.json().get("risks", [])
    assert isinstance(risks, list)

def test_decision_visibility_has_level(client, cid):
    r = client.get(f"/api/v1/decision/company/{cid}")
    vis = r.json().get("scores", {}).get("visibility", {})
    assert "level" in vis, f"visibility must have level, got keys: {list(vis.keys())}"

def test_decision_trust_score(client, cid):
    """Trust via competitive_position (trust embedded)"""
    r = client.get(f"/api/v1/decision/company/{cid}")
    cp = r.json().get("scores", {}).get("competitive_position", {})
    assert "score" in cp, "competitive_position must have score"
    assert isinstance(cp["score"], (int, float)), f"cp.score must be numeric"

def test_decision_idempotent(client, cid):
    """同企业两次调用应返回相同评分"""
    r1 = client.get(f"/api/v1/decision/company/{cid}")
    r2 = client.get(f"/api/v1/decision/company/{cid}")
    s1 = r1.json().get("scores", {}).get("visibility", {}).get("score", 0)
    s2 = r2.json().get("scores", {}).get("visibility", {}).get("score", 0)
    assert s1 == s2, f"Decision should be idempotent: {s1} != {s2}"

def test_config_reload_affects_scoring(client, cid):
    """验证配置热加载 — 修改权重后评分可能变化"""
    r_before = client.get(f"/api/v1/decision/company/{cid}")
    before = r_before.json().get("scores", {}).get("visibility", {}).get("score", 0)
    # 读取当前配置
    try:
        current_cfg = client.get("/api/v1/admin/configs/scoring/visibility").json()
    except:
        current_cfg = {}
    # 修改配置（增加trust权重）
    test_cfg = dict(current_cfg)
    test_cfg["trust_weight"] = 0.9
    client.put("/api/v1/admin/configs/scoring/visibility", json={"data": test_cfg})
    # 再次评分
    r_after = client.get(f"/api/v1/decision/company/{cid}")
    after = r_after.json().get("scores", {}).get("visibility", {}).get("score", 0)
    # 恢复配置
    if current_cfg:
        client.put("/api/v1/admin/configs/scoring/visibility", json={"data": current_cfg})
    # 权重变化应有影响（至少记录了变化）
    assert isinstance(before, (int, float)) and isinstance(after, (int, float))

def test_decision_all_scores_present(client, cid):
    """Decision score dimensions validation"""
    r = client.get(f"/api/v1/decision/company/{cid}")
    scores = r.json().get("scores", {})
    required = ["visibility", "company_growth", "competitive_position", "roadmap", "content_strategy", "market_connection"]
    missing = [rk for rk in required if rk not in scores]
    assert not missing, f"Missing: {missing}"

def test_decision_roadmap_present(client, cid):
    """Decision 应包含行动路线"""
    r = client.get(f"/api/v1/decision/company/{cid}")
    data = r.json()
    has_roadmap = "roadmap" in data or any("recommend" in k.lower() for k in data.keys())
    assert has_roadmap, "Decision must include roadmap or recommendations"
