import pytest

def test_context_company(client, company_id):
    r = client.get(f"/api/v1/context/company/{company_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["company"]["id"] == company_id
    assert "capabilities" in data
    assert "evidence" in data
    assert "scoring" in data

def test_decision_company(client, company_id):
    r = client.get(f"/api/v1/decision/company/{company_id}")
    assert r.status_code == 200
    data = r.json()
    assert "geo_score" in data or "scores" in data

def test_agent_analyze(client, company_id):
    r = client.post("/api/v1/agent/analyze", json={
        "entity_type": "company",
        "entity_id": company_id,
        "query": "分析企业GEO竞争力"
    })
    assert r.status_code == 200
    data = r.json()
    # Agent endpoint returns 200 with structured response\n    assert "agent" in data\n    assert "intent" in data

def test_context_query(client):
    r = client.get(f"/api/v1/context/company/{client.get('/api/v1/companies/?limit=1').json()[0]['id']}")
    assert r.status_code == 200
    data = r.json()
    assert "company" in data
    assert "scoring" in data

def test_admin_companies(client):
    r = client.get("/api/v1/admin/companies")
    assert r.status_code == 200
    assert len(r.json()) >= 1


