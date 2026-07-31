import pytest
from sqlalchemy import select
from app.decision.matching import GEOMatchingEngine
from app.models.market_demand import MarketDemand
from app.models.provider import Provider
from app.models.match_result import MatchResult
from app.database import _get_session_factory

@pytest.fixture
def engine():
    return GEOMatchingEngine()

@pytest.mark.asyncio
async def test_engine_initialization(engine):
    assert engine.config is not None
    assert "weights" in engine.config
    assert engine.config["weights"]["capability_overlap"] == 0.25

@pytest.mark.asyncio
async def test_weights_are_configurable(engine):
    w = engine._get_weights()
    assert abs(sum(w.values()) - 1.0) < 0.01

@pytest.mark.asyncio
async def test_match_with_no_demand(engine):
    factory = _get_session_factory()
    async with factory() as session:
        with pytest.raises(ValueError, match="not found"):
            await engine.match("00000000-0000-0000-0000-000000000000", session)

@pytest.mark.asyncio
async def test_match_with_real_data(engine):
    factory = _get_session_factory()
    async with factory() as session:
        demands = (await session.execute(select(MarketDemand).limit(1))).scalars().all()
        if not demands:
            pytest.skip("No demands in DB - run seed_providers.py first")
        result = await engine.match(str(demands[0].id), session)
        assert "demand_id" in result
        assert isinstance(result["matches"], list)

@pytest.mark.asyncio
async def test_weight_reload(engine):
    orig_w = dict(engine._get_weights())
    engine.config["weights"]["trust_score"] = 0.15
    assert engine._get_weights()["trust_score"] == 0.15
    engine.config["weights"] = orig_w

@pytest.mark.asyncio
async def test_match_result_has_reasons(engine):
    factory = _get_session_factory()
    async with factory() as session:
        demands = (await session.execute(select(MarketDemand).limit(1))).scalars().all()
        if not demands:
            pytest.skip("No demands in DB")
        result = await engine.match(str(demands[0].id), session)
        for m in result["matches"]:
            assert "reasons" in m
            assert "score" in m
            assert "level" in m

@pytest.mark.asyncio
async def test_engine_reload_weights(engine):
    engine.reload_weights()
    assert engine.config is not None

@pytest.mark.asyncio
async def test_providers_exist():
    factory = _get_session_factory()
    async with factory() as session:
        providers = (await session.execute(select(Provider).limit(1))).scalars().all()
        if not providers:
            pytest.skip("No providers in DB - run seed_providers.py first")
        assert len(providers) > 0
