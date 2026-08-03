import pytest
import asyncio
from app.config import Config
from app.engine import Engine
from app.adapters.registry import get_adapter, reset_cache
from app.adapters.mock_adapter import MockAdapter
from app.merge import MergeEngine
from app.validator import validate
from app.baseline import BaselineBuilder
from app.scheduler import Scheduler
from app.perspective_engine import analyze, available_perspectives
from util.logger import Logger


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def logger():
    return Logger()


@pytest.fixture
def adapter():
    return MockAdapter()


@pytest.fixture
def engine(config, adapter, logger):
    return Engine(config=config, adapter=adapter, logger=logger)


def test_config_loads(config):
    assert "provider" in config.base
    assert "direct" in config.tracks
    assert "validation" in config.tracks
    assert "perspective" in config.tracks


@pytest.mark.asyncio
async def test_mock_adapter_generate(adapter):
    result = await adapter.generate("test prompt")
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_mock_adapter_health(adapter):
    assert await adapter.health_check() is True


def test_mock_adapter_token_usage(adapter):
    usage = adapter.token_usage()
    assert "prompt_tokens" in usage
    assert "completion_tokens" in usage


@pytest.mark.asyncio
async def test_registry_fallback():
    reset_cache()
    adapter = await get_adapter("nonexistent")
    assert isinstance(adapter, MockAdapter)


@pytest.mark.asyncio
async def test_registry_get_mock():
    reset_cache()
    adapter = await get_adapter("mock")
    assert isinstance(adapter, MockAdapter)


def test_baseline_builder():
    builder = BaselineBuilder()
    ctx = builder.build("hello world")
    assert ctx["request"] == "hello world"
    assert "meta" in ctx
    assert "now" in ctx["meta"]


def test_scheduler(config):
    scheduler = Scheduler(config)
    tracks = scheduler.schedule()
    assert "direct" in tracks
    assert "validation" in tracks
    assert "perspective" in tracks


def test_merge_engine_prefers_direct():
    merge = MergeEngine()
    outputs = [
        {"track": "validation", "answer": "val answer"},
        {"track": "direct", "answer": "direct answer"},
        {"track": "perspective", "answer": "persp answer"},
    ]
    result = merge.merge(outputs)
    assert result["answer"] == "direct answer"
    assert "direct" in result["sources"]


def test_merge_engine_fallback_to_perspective():
    merge = MergeEngine()
    outputs = [
        {"track": "validation", "answer": "val answer"},
        {"track": "perspective", "answer": "persp answer"},
    ]
    result = merge.merge(outputs)
    assert result["answer"] == "persp answer"


def test_merge_engine_fallback_to_first():
    merge = MergeEngine()
    outputs = [
        {"track": "validation", "answer": "val answer"},
    ]
    result = merge.merge(outputs)
    assert result["answer"] == "val answer"


@pytest.mark.asyncio
async def test_validator_passes(adapter):
    result = await validate("What is 2+2?", "The answer is 4.", adapter, second_sample=False)
    assert result.passed is True
    assert isinstance(result.confidence, int)
    assert isinstance(result.drift, float)


@pytest.mark.asyncio
async def test_engine_run(engine):
    result = await engine.run("test request")
    assert "answer" in result
    assert "validation" in result
    assert "timing" in result
    assert "total_ms" in result["timing"]


@pytest.mark.asyncio
async def test_engine_run_track(engine):
    ctx = {"request": "hello", "meta": {"now": 123}}
    result = await engine.run_track("direct", ctx)
    assert result["track"] == "direct"
    assert "answer" in result


@pytest.mark.asyncio
async def test_engine_validation_structure(engine):
    result = await engine.run("test")
    v = result["validation"]
    assert "pass" in v
    assert "confidence" in v
    assert "drift" in v
    assert "notes" in v


def test_perspectives_count():
    assert len(available_perspectives()) == 12


@pytest.mark.asyncio
async def test_perspectives_run(adapter):
    results = await analyze("test", adapter, mode="subset", subset=["engineering"])
    assert len(results) == 1
    assert results[0].name == "engineering"
