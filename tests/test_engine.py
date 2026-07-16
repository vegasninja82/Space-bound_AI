import pytest
import asyncio
from app.config import Config
from app.engine import Engine
from app.adapters.registry import AdapterRegistry
from app.adapters.mock_adapter import MockAdapter
from app.merge import MergeEngine
from app.validator import Validator
from app.baseline import BaselineBuilder
from app.scheduler import Scheduler
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


def test_mock_adapter_generate(adapter):
    result = adapter.generate("test prompt")
    assert "MOCK_ANSWER" in result
    assert "test prompt" in result


def test_mock_adapter_health(adapter):
    assert adapter.health_check() is True


def test_mock_adapter_token_usage(adapter):
    usage = adapter.token_usage()
    assert "prompt_tokens" in usage
    assert "completion_tokens" in usage


def test_registry_fallback(config):
    registry = AdapterRegistry(config)
    adapter = registry.get("nonexistent")
    assert isinstance(adapter, MockAdapter)


def test_registry_get_mock(config):
    registry = AdapterRegistry(config)
    adapter = registry.get("mock")
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


def test_validator_passes():
    validator = Validator()
    result = validator.validate({"answer": "test"})
    assert result["pass"] is True
    assert "confidence" in result
    assert "drift" in result


def test_engine_run(engine):
    result = asyncio.run(engine.run("test request"))
    assert "answer" in result
    assert "validation" in result
    assert "timing" in result
    assert "total_ms" in result["timing"]
    assert "MOCK_ANSWER" in result["answer"]


def test_engine_run_track(engine):
    ctx = {"request": "hello", "meta": {"now": 123}}
    result = asyncio.run(engine.run_track("direct", ctx))
    assert result["track"] == "direct"
    assert "answer" in result


def test_engine_validation_structure(engine):
    result = asyncio.run(engine.run("test"))
    v = result["validation"]
    assert "pass" in v
    assert "confidence" in v
    assert "drift" in v
    assert "notes" in v
