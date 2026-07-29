"""API contract completeness tests"""
import pytest
import importlib
from fastapi.testclient import TestClient

EXPECTED_ROUTERS = ["agent","auth","users","entities","companies","industries","relationships","evidence","context","decision","admin","mcp_router","analytics","certification","subscriptions","marketplace","intelligence","payments"]

@pytest.fixture
def app():
    from app.main import app
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_api_docs_accessible(client):
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "paths" in spec and len(spec["paths"]) > 0

def test_all_routers_importable():
    for router_name in EXPECTED_ROUTERS:
        mod = importlib.import_module(f"app.api.v1.{router_name}")
        assert hasattr(mod, "router"), f"{router_name} missing router"

def test_all_routers_registered(app):
    routes = [r.path for r in app.routes]
    assert any("/api/v1/auth" in r for r in routes)
    assert any("/api/v1/companies" in r for r in routes)
    assert any("/api/v1/entities" in r for r in routes)
    assert any("/api/v1/decision" in r for r in routes)
    assert any("/api/v1/certification" in r for r in routes)
    assert any("/api/v1/marketplace" in r for r in routes)
    assert any("/api/v1/intelligence" in r for r in routes)
