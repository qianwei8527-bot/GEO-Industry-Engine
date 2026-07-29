"""ORM Model import and structure tests"""
import pytest
import importlib

EXPECTED_MODELS = {
    "user": "User",
    "industry": "Industry",
    "entity": "Entity",
    "company": "Company",
    "capability": "Capability",
    "relationship": "Relationship",
    "event": "Event",
    "evidence": "Evidence",
    "analytics_event": "AnalyticsEvent",
    "certification": "Certification",
    "subscription": "Subscription",
    "order": "Order",
    "payment_transaction": "PaymentTransaction",
    "market_demand": "MarketDemand",
    "transaction_review": "TransactionReview",
    "competitor": "Competitor",
}

def test_all_models_importable():
    from app.database import Base
    for mod_name, cls_name in EXPECTED_MODELS.items():
        mod = importlib.import_module(f"app.models.{mod_name}")
        model = getattr(mod, cls_name)
        assert model is not None
        assert hasattr(model, "__tablename__")

def test_all_models_inherit_base():
    from app.database import Base
    for mod_name, cls_name in EXPECTED_MODELS.items():
        mod = importlib.import_module(f"app.models.{mod_name}")
        model = getattr(mod, cls_name)
        assert issubclass(model, Base)

def test_model_schema_mapping():
    schema_dir = r"D:\GEO-IE\backend\app\schemas"
    import os
    schemas = [f.replace(".py", "") for f in os.listdir(schema_dir) if f.endswith(".py") and not f.startswith("__")]
    # Verify all 6 previously-missing schemas exist
    required = ["event", "analytics_event", "marketplace", "payment", "order", "transaction_review"]
    for s in required:
        assert s in schemas, f"Missing schema: {s}"
