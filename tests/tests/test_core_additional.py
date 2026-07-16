import pytest
import asyncio

from app.validator import Validator
from app.merge import MergeEngine
from app.scheduler import Scheduler
from app.adapters.mock_adapter import MockAdapter
from app.adapters.registry import AdapterRegistry
from app.metrics import MetricsRecorder
from app.config import Config
from app.baseline import BaselineBuilder
from app.engine import Engine
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
    return Engine(
        config=config,
        adapter=adapter,
        logger=logger
    )


# -----------------------------
# Validator tests
# -----------------------------

def test_validator_empty_answer():
    validator = Validator()
    result = validator.validate({"answer": ""})
    assert "pass" in result
    assert "confidence" in result


def test_validator_normal_answer():
    validator = Validator()
    result = validator.validate(
        {"answer": "A complete response"}
    )
    assert result["pass"] is True


def test_validator_contains_metrics():
    validator = Validator()
    result = validator.validate(
        {"answer": "test"}
    )
    assert "confidence" in result
    assert "drift" in result
    assert "notes" in result


# -----------------------------
# Merge tests
# -----------------------------

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
    result = merge.merge([
        {"track": "direct", "answer": "answer"}
    ])
    assert "sources" in result


# -----------------------------
# Scheduler tests
# -----------------------------

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


# -----------------------------
# Adapter tests
# -----------------------------

def test_adapter_generate_multiple(adapter):
    result = adapter.generate("hello")
    assert isinstance(result, str)


def test_adapter_health_boolean(adapter):
    assert isinstance(
        adapter.health_check(),
        bool
    )


def test_adapter_usage_structure(adapter):
    usage = adapter.token_usage()
    assert isinstance(usage, dict)


def test_registry_mock_provider(config):
    registry = AdapterRegistry(config)
    result = registry.get("mock")
    assert isinstance(result, MockAdapter)


def test_registry_unknown_provider(config):
    registry = AdapterRegistry(config)
    result = registry.get("unknown")
    assert isinstance(result, MockAdapter)


# -----------------------------
# Baseline tests
# -----------------------------

def test_baseline_metadata():
    builder = BaselineBuilder()
    result = builder.build("test")

    assert "meta" in result
    assert "now" in result["meta"]


def test_baseline_request_storage():
    builder = BaselineBuilder()
    result = builder.build("hello")

    assert result["request"] == "hello"


# -----------------------------
# Engine integration tests
# -----------------------------

def test_engine_returns_validation(engine):
    result = asyncio.run(
        engine.run("integration test")
    )

    assert "validation" in result


def test_engine_returns_timing(engine):
    result = asyncio.run(
        engine.run("timing test")
    )

    assert "timing" in result


def test_engine_returns_answer(engine):
    result = asyncio.run(
        engine.run("answer test")
    )

    assert "answer" in result


def test_engine_track_execution(engine):
    ctx = {
        "request": "track",
        "meta": {"now": 1}
    }

    result = asyncio.run(
        engine.run_track(
            "direct",
            ctx
        )
    )

    assert result["track"] == "direct"


# -----------------------------
# Regression tests
# -----------------------------

def test_mock_provider_is_deterministic(adapter):
    first = adapter.generate("same")
    second = adapter.generate("same")

    assert first == second


def test_config_object_exists(config):
    assert config is not None


def test_logger_exists(logger):
    assert logger is not None


def test_engine_object_exists(engine):
    assert engine is not None
