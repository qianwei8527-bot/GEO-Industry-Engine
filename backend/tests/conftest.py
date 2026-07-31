import pytest
import httpx
import asyncio
from app.database import _get_session_factory

BASE_URL = "http://127.0.0.1:8080"

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL

@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10) as c:
        yield c

@pytest.fixture(scope="session")
def company_id(client):
    r = client.get("/api/v1/companies/?limit=1")
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    return data[0]["id"]

@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    """Async DB session for tests that need database access."""
    factory = _get_session_factory()
    async with factory() as session:
        yield session
