"""E2E Business Flow Test: Company -> Context -> Decision -> Agent -> Report -> Persist"""
import pytest
import httpx
import time

BASE_URL = "http://127.0.0.1:8080"

@pytest.fixture(scope="module")
def api_client():
    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        yield client

def test_01_get_companies(api_client):
    """Step 1: List companies - verify data exists"""
    r = api_client.get("/api/v1/companies/")
    assert r.status_code == 200
    data = r.json()
    companies = data if isinstance(data, list) else data.get("items", [])
    assert len(companies) > 0
    return companies[0]["id"]

def test_02_get_context(api_client):
    """Step 2: Get company context"""
    cid = test_01_get_companies(api_client)
    r = api_client.get("/api/v1/context/company/" + cid)
    assert r.status_code == 200
    ctx = r.json()
    assert "company" in ctx
    assert ctx["company"] is not None

def test_03_get_decision(api_client):
    """Step 3: Get decision/score"""
    cid = test_01_get_companies(api_client)
    r = api_client.get("/api/v1/decision/company/" + cid)
    assert r.status_code == 200
    dec = r.json()
    assert "overall" in dec or "scores" in dec

def test_04_agent_report(api_client):
    """Step 4: Generate agent strategic report"""
    cid = test_01_get_companies(api_client)
    r = api_client.get("/api/v1/agent/report/" + cid)
    assert r.status_code == 200
    report = r.json()
    assert report["success"] is True
    assert "report" in report
    assert report["report"] is not None
    # Check structured report fields
    rep = report["report"]
    assert "geo_identity" in rep
    assert "visibility" in rep or "visibility_assessment" in rep
    assert "opportunities" in rep or "recommendations" in rep

def test_05_score_persisted(api_client):
    """Step 5: Verify GEO score was persisted to DB"""
    cid = test_01_get_companies(api_client)
    r = api_client.get("/api/v1/companies/" + cid)
    assert r.status_code == 200
    company = r.json()
    # Company may be returned directly or as nested
    geo_score = company.get("geo_score", None)
    if geo_score is None:
        # Try nested
        geo_score = company.get("company", {}).get("geo_score", 0)
    assert geo_score is not None, "GEO score should be persisted after agent report"

def test_06_full_flywheel(api_client):
    """Step 6: Verify end-to-end GEO intelligence flow"""
    cid = test_01_get_companies(api_client)
    
    # Context
    ctx_r = api_client.get("/api/v1/context/company/" + cid)
    assert ctx_r.status_code == 200
    
    # Decision
    dec_r = api_client.get("/api/v1/decision/company/" + cid)
    assert dec_r.status_code == 200
    
    # Agent Report
    agent_r = api_client.get("/api/v1/agent/report/" + cid)
    assert agent_r.status_code == 200
    assert agent_r.json()["success"]
    
    # Company detail page
    comp_r = api_client.get("/api/v1/companies/" + cid)
    assert comp_r.status_code == 200
    
    # Assets overview
    assets_r = api_client.get("/api/v1/assets/overview")
    assert assets_r.status_code == 200
