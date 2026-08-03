import pytest
import asyncio
from app.adapters.mock_adapter import MockAdapter
from app.validator import validate
from app.merge import MergeEngine
from app.scheduler import Scheduler
from app.adapters.registry import get_adapter, available_providers, reset_cache
from app.config import Config
from app.baseline import BaselineBuilder
from app.engine import Engine
from app.perspective_engine import analyze, available_perspectives
from util.logger import Logger


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def adapter():
    return MockAdapter()


@pytest.fixture
def logger():
    return Logger()


@pytest.fixture
def engine(config, adapter, logger):
    return Engine(config=config, adapter=adapter, logger=logger)


# Validator tests
@pytest.mark.asyncio
async def test_validator_empty_answer(adapter):
    result = await validate("", "", adapter, second_sample=False)
    assert result.passed is False


@pytest.mark.asyncio
async def test_validator_normal_answer(adapter):
    result = await validate("What is 2+2?", "The answer is 4.", adapter, second_sample=False)
    assert result.passed is True
    assert result.confidence >= 60


@pytest.mark.asyncio
async def test_validator_contains_metrics(adapter):
    result = await validate("test prompt", "A response.", adapter, second_sample=False)
    assert isinstance(result.confidence, int)
    assert isinstance(result.drift, float)
    assert isinstance(result.notes, list)
    assert isinstance(result.signals, dict)


# Merge tests
def test_merge_empty_results():
    merge = MergeEngine()
    result = merge.merge([])
    assert "answer" in result


def test_merge_direct_priority():
    merge = MergeEngine()
    result = merge.merge([
        {"track": "perspective", "answer": "perspective"},
        {"track": "direct", "answer": "direct"},
    ])
    assert result["answer"] == "direct"


def test_merge_source_tracking():
    merge = MergeEngine()
    result = merge.merge([{"track": "direct", "answer": "answer"}])
    assert "sources" in result


# Scheduler tests
def test_scheduler_returns_tracks(config):
    scheduler = Scheduler(config)
    tracks = scheduler.schedule()
    assert isinstance(tracks, list)
    assert len(tracks) >= 3


def test_scheduler_direct_exists(config):
    scheduler = Scheduler(config)
    assert "direct" in scheduler.schedule()


def test_scheduler_validation_exists(config):
    scheduler = Scheduler(config)
    assert "validation" in scheduler.schedule()


# Adapter tests
@pytest.mark.asyncio
async def test_adapter_generate_multiple(adapter):
    result = await adapter.generate("hello")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_adapter_health_boolean(adapter):
    ok = await adapter.health_check()
    assert isinstance(ok, bool)


def test_adapter_usage_structure(adapter):
    usage = adapter.token_usage()
    assert isinstance(usage, dict)


@pytest.mark.asyncio
async def test_registry_mock_provider():
    reset_cache()
    adapter = await get_adapter("mock")
    assert isinstance(adapter, MockAdapter)


@pytest.mark.asyncio
async def test_registry_unknown_provider():
    reset_cache()
    adapter = await get_adapter("unknown")
    assert isinstance(adapter, MockAdapter)


# Perspective tests
@pytest.mark.asyncio
async def test_perspectives_subset(adapter):
    results = await analyze("test prompt", adapter, mode="subset", subset=["engineering", "security"])
    assert len(results) == 2


@pytest.mark.asyncio
async def test_perspectives_all(adapter):
    results = await analyze("test prompt", adapter, mode="all")
    assert len(results) == 12


# Baseline tests
def test_baseline_metadata():
    builder = BaselineBuilder()
    result = builder.build("test")
    assert "meta" in result
    assert "now" in result["meta"]


def test_baseline_request_storage():
    builder = BaselineBuilder()
    result = builder.build("hello")
    assert result["request"] == "hello"


# Engine tests
@pytest.mark.asyncio
async def test_engine_returns_validation(engine):
    result = await engine.run("integration test")
    assert "validation" in result


@pytest.mark.asyncio
async def test_engine_returns_timing(engine):
    result = await engine.run("timing test")
    assert "timing" in result


@pytest.mark.asyncio
async def test_engine_returns_answer(engine):
    result = await engine.run("answer test")
    assert "answer" in result


@pytest.mark.asyncio
async def test_engine_track_execution(engine):
    ctx = {"request": "track", "meta": {"now": 1}}
    result = await engine.run_track("direct", ctx)
    assert result["track"] == "direct"


# Regression tests
@pytest.mark.asyncio
async def test_mock_provider_is_deterministic(adapter):
    first = await adapter.generate("same")
    second = await adapter.generate("same")
    assert first == second


def test_config_object_exists(config):
    assert config is not None


def test_logger_exists(logger):
    assert logger is not None


def test_engine_object_exists(engine):
    assert engine is not None
