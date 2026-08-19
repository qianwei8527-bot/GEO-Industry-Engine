"""Pydantic Schema architecture validation tests"""
import pytest
import uuid
from datetime import datetime

def test_event_schema_import():
    from app.schemas.event import EventCreate, EventResponse, EventSummary
    assert EventCreate is not None

def test_analytics_event_schema_import():
    from app.schemas.analytics_event import AnalyticsEventCreate, AnalyticsEventBatch, AnalyticsEventResponse, AnalyticsSummary
    assert AnalyticsEventCreate is not None

def test_marketplace_schema_import():
    from app.schemas.marketplace import MarketDemandCreate, MarketDemandResponse, ReviewCreate, ReviewResponse
    assert MarketDemandCreate is not None

def test_payment_schema_import():
    from app.schemas.payment import PaymentTransactionResponse, PaymentCallbackPayload, PaymentStatusEnum
    assert PaymentStatusEnum.succeeded.value == "succeeded"

def test_order_schema_import():
    from app.schemas.order import OrderCreate, OrderResponse, OrderTypeEnum, OrderStatusEnum
    assert OrderTypeEnum.subscription_new.value == "subscription_new"

def test_transaction_review_schema_import():
    from app.schemas.transaction_review import TransactionReviewResponse, ReviewSummary
    assert TransactionReviewResponse is not None

def test_event_create_valid():
    from app.schemas.event import EventCreate
    e = EventCreate(entity_id=uuid.uuid4(), event_type="product_launch", title="Test Event", occurred_at=datetime.utcnow(), description="A test event", impact_level=5)
    assert e.event_type == "product_launch" and e.impact_level == 5

def test_event_create_invalid_impact():
    from app.schemas.event import EventCreate
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        EventCreate(entity_id=uuid.uuid4(), event_type="test", title="Test", occurred_at=datetime.utcnow(), impact_level=99)

def test_order_create_valid():
    from app.schemas.order import OrderCreate, OrderTypeEnum
    o = OrderCreate(order_type=OrderTypeEnum.subscription_new, amount=99.00)
    assert o.amount == 99.00 and o.currency == "CNY"
