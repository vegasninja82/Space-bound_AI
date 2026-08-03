"""
Sandbox-only smoke test for SPACE_BOUND_AI.

NOT shipped in production — validates all core components
end-to-end with deterministic mocks and local storage.

Usage:
  PYTHONPATH=. python tests/smoke_test.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def main():
    failures = []

    def check(label, cond):
        status = "OK" if cond else "FAIL"
        if not cond:
            failures.append(label)
        print(f"[{status}] {label}")

    print("=" * 70)
    print("SPACE_BOUND_AI Smoke Test (Sandbox Only)")
    print("=" * 70)
    print()

    # --- config ---
    print("→ Testing config...")
    from app.config import Config
    cfg = Config()
    check("config: provider default loaded", cfg.base.get("provider") == "mock")
    check("config: tracks loaded", "direct" in cfg.tracks and "validation" in cfg.tracks)

    # --- mock adapter ---
    print("→ Testing mock adapter...")
    from app.adapters.mock_adapter import MockAdapter
    m = MockAdapter()
    t1 = await m.generate("Explain quantum computing simply.")
    t2 = await m.generate("Explain quantum computing simply.")
    check("mock adapter: deterministic for same prompt", t1 == t2)

    # --- validator ---
    print("→ Testing validator...")
    from app.validator import validate
    result_clean = await validate("What is 2+2?", "The answer is 4.", m, second_sample=False)
    check("validator: clean answer passes", result_clean.passed is True)
    check("validator: confidence >= 60", result_clean.confidence >= 60)

    result_empty = await validate("", "", m, second_sample=False)
    check("validator: empty answer fails", result_empty.passed is False)

    # --- perspective engine ---
    print("→ Testing perspective engine...")
    from app.perspective_engine import analyze, available_perspectives
    perspectives = available_perspectives()
    check("perspectives: 12 lenses defined", len(perspectives) == 12)
    check("perspectives: includes engineering", "engineering" in perspectives)
    check("perspectives: includes security", "security" in perspectives)

    results = await analyze("test prompt", m, mode="subset", subset=["engineering", "security"])
    check("perspectives: subset returns 2", len(results) == 2)

    # --- merge engine ---
    print("→ Testing merge engine...")
    from app.merge import MergeEngine
    merge = MergeEngine()

    result_priority = merge.merge([
        {"track": "perspective", "answer": "perspective view"},
        {"track": "direct", "answer": "direct answer"},
    ])
    check("merge: direct track has priority", result_priority["answer"] == "direct answer")
    check("merge: sources tracked", "direct" in result_priority["sources"])

    result_fallback = merge.merge([
        {"track": "validation", "answer": "validation view"},
        {"track": "perspective", "answer": "perspective view"},
    ])
    check("merge: perspective takes precedence over validation", result_fallback["answer"] == "perspective view")

    # --- reality feed ---
    print("→ Testing reality feed...")
    from app.reality_feed import RealityFeed
    rf = RealityFeed(endpoint="http://localhost:8081/sensor")
    state = await rf.get_live_actuality()
    check("reality feed: returns state dict", isinstance(state, dict))
    check("reality feed: has safety defaults", "green_light" in state)
    await rf.close()

    # --- crucible (ZeroHourGate) ---
    print("→ Testing ZeroHourGate...")
    from app.crucible import ZeroHourGate
    gate = ZeroHourGate()

    safe_payload = {
        "response": "Proceeding with caution.",
        "assumptions": [],
        "metadata": {"execution_status": "PENDING"},
        "confidence": 85
    }

    class MockTarget:
        async def transmit(self, payload):
            return payload

    result_safe = await gate.verify_and_transmit(safe_payload, MockTarget())
    check("crucible: empty assumptions passes", result_safe.get("metadata", {}).get("execution_status") != "EXCEPTION_INTERCEPTED")

    # --- adapter registry ---
    print("→ Testing adapter registry...")
    from app.adapters.registry import get_adapter, available_providers, reset_cache
    reset_cache()
    mock_adapter = await get_adapter("mock")
    check("registry: returns mock adapter", isinstance(mock_adapter, MockAdapter))

    unknown_adapter = await get_adapter("unknown_provider")
    check("registry: falls back to mock for unknown", isinstance(unknown_adapter, MockAdapter))

    # --- engine end-to-end ---
    print("→ Testing engine orchestration...")
    from app.engine import Engine
    engine = Engine(config=cfg, adapter=MockAdapter(), logger=None)
    result = await engine.run("Test request")
    check("engine: returns answer", "answer" in result)
    check("engine: includes validation", "validation" in result)
    check("engine: includes timing", "timing" in result and "total_ms" in result["timing"])
    check("engine: lists sources", "sources" in result and isinstance(result["sources"], list))

    print()
    print("=" * 70)
    if failures:
        print(f"❌ {len(failures)} FAILURE(S):")
        for f in failures:
            print(f"   - {f}")
        sys.exit(1)
    else:
        print("✅ ALL CHECKS PASSED")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
