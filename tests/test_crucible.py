# tests/test_crucible.py
import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.reality_feed import RealityFeed, Actuality
from app.crucible import ZeroHourGate
@pytest.mark.asyncio
async def test_zero_hour_timeout_fallback():
    """
    PROVES: Path 2 & 3 boundary enforcement.
    If external sensor APIs latency spikes to 200ms, the RealityFeed must 
    intercept the timeout within 50ms and fall back cleanly to SAFE_DEFAULT.
    """
    feed = RealityFeed()
    
    # Simulate a severe network lag on the sensor endpoints
    async def artificial_hang(*args, **kwargs):
        await asyncio.sleep(0.200) # 200ms latency spike
        mock_response = MagicMock()
        mock_response.json.return_value = {"green": True, "status": "CLEAR"}
        mock_response.status_code = 200
        return mock_response
    feed._client.get = AsyncMock(side_effect=artificial_hang)
    
    start_time = time.time()
    # Trigger the live read. Cache is empty, forcing a fast refresh loop.
    actual_state = await feed.get_live_actuality()
    execution_duration_ms = (time.time() - start_time) * 1000
    # Assertions: System must break out long before the 200ms hang completes
    assert execution_duration_ms < 60.0, f"Deadline violated: Gate took {execution_duration_ms}ms"
    assert actual_state == feed.SAFE_DEFAULT
    assert actual_state["green_light"] is False  # Fail-closed state enforced
    
    await feed.close()
@pytest.mark.asyncio
async def test_exception_intercept_override():
    """
    PROVES: Structural resilience against raw network exceptions.
    If a local sensor endpoint drops its socket or throws a connection error, 
    asyncio.gather must absorb the exception and proceed with safe defaults.
    """
    feed = RealityFeed()
    
    # Simulate a hard socket crash/connection refused exception
    feed._client.get = AsyncMock(side_effect=ConnectionRefusedError("Socket violently closed by remote host"))
    
    # Warmup pass must complete successfully without raising unhandled exceptions
    await feed.warmup()
    
    actual_state = await feed.get_live_actuality()
    
    # Assertions: The crash must be completely encapsulated
    assert actual_state == feed.SAFE_DEFAULT
    assert actual_state["system_nominal"] is False
    assert actual_state["cross_traffic"] == "UNKNOWN"
    
    await feed.close()
@pytest.mark.asyncio
async def test_cache_ttl_freshness_boundary():
    """
    PROVES: Path 1 atomic execution.
    If the data cache is fresher than 100ms, get_live_actuality must execute 
    an instantaneous local memory read (0ms), skipping the network entirely.
    """
    feed = RealityFeed()
    
    # Pre-populate the internal cache with an uncompromised, fresh timestamp
    fresh_snapshot = {
        "green_light": True,
        "cross_traffic": "NONE",
        "system_nominal": True
    }
    feed._cache = Actuality(data=fresh_snapshot, timestamp=time.time() * 1000)
    
    # If the engine erroneously attempts a network call on a fresh cache, explode the test
    feed._client.get = AsyncMock(side_effect=AssertionError("Hot-path error: Hit network for fresh cache!"))
    
    start_time = time.time()
    actual_state = await feed.get_live_actuality()
    execution_duration_ms = (time.time() - start_time) * 1000
    
    # Assertions: Must be a near-instantaneous memory swap
    assert execution_duration_ms < 2.0
    assert actual_state["green_light"] is True
    assert actual_state["cross_traffic"] == "NONE"
    
    await feed.close()
@pytest.mark.asyncio
async def test_zero_hour_gate_veto_execution():
    """
    PROVES: The Collision Check mechanism inside ZeroHourGate.
    If the payload assumes green_light is True, but the reality feed detects 
    an inversion, the gate must intercept and rewrite the payload with a Z-12 HALT.
    """
    gate = ZeroHourGate()
    
    # Mock reality feed to explicitly return an inverted environment state
    gate.reality_feed.get_live_actuality = AsyncMock(return_value={
        "green_light": False, # Red light runner / signal change occurred
        "cross_traffic": "DETECTED",
        "system_nominal": True
    })
    
    # Formulate a payload carrying a self-projected assumption of safety
    mock_payload = {
        "response": "The light is green, proceeding through the intersection safely.",
        "assumptions": ["green_light", "no_cross_traffic"],
        "metadata": {"execution_status": "PENDING"},
        "confidence": 0.98
    }
    
    mock_execution_target = AsyncMock()
    
    final_output = await gate.verify_and_transmit(
        synthesized_payload=mock_payload,
        execution_target=mock_execution_target
    )
    
    # Assertions: Target transmission must never be called, payload must be rewritten
    mock_execution_target.transmit.assert_not_called()
    assert final_output["metadata"]["execution_status"] == "EXCEPTION_INTERCEPTED"
    assert final_output["metadata"]["veto_reason"] == "green_light_INVERTED"
    assert "Z-12 HALT" in final_output["response"]
    assert final_output["confidence"] == 0.0
    
    await gate.reality_feed.close()
