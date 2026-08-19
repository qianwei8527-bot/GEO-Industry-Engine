import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from app.api.v1.providers import _to_response


def test_provider_response_serializes_extra_data_as_metadata():
    provider = SimpleNamespace(
        id=uuid.uuid4(),
        entity_id=uuid.uuid4(),
        provider_type="company",
        trust_score=12.0,
        geo_score=24.0,
        verification_status="verified",
        is_verified=False,
        is_active=True,
        completed_orders=0,
        avg_rating=0.0,
        pricing_model=None,
        extra_data={"region": "shenzhen"},
        created_at=datetime.now(timezone.utc),
    )
    response = _to_response(provider)
    assert response.metadata == {"region": "shenzhen"}
