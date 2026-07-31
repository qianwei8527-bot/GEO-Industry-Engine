import pytest

def test_list_companies(client):
    r = client.get("/api/v1/companies/?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert "name" in data[0]
    assert "geo_id" in data[0]

def test_get_company_detail(client, company_id):
    r = client.get(f"/api/v1/companies/{company_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == company_id
    assert "name" in data
    assert "subscription_tier" in data

def test_list_industries(client):
    r = client.get("/api/v1/industries/")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_list_entities(client):
    r = client.get("/api/v1/entities/?limit=5")
    assert r.status_code == 200
    assert len(r.json()) >= 1

def test_list_evidence(client):
    r = client.get("/api/v1/evidence/?limit=5")
    assert r.status_code == 200

def test_admin_health(client):
    r = client.get("/api/v1/admin/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_admin_db_stats(client):
    r = client.get("/api/v1/admin/db-stats")
    assert r.status_code == 200
    assert r.json()["total"] > 0

def test_admin_configs(client):
    r = client.get("/api/v1/admin/configs")
    assert r.status_code == 200
    data = r.json()
    assert "scoring" in data
