"""
Single entry point the rest of the app uses to get a provider. Real
fallback logic: missing package, missing API key, or a failed health
check all land on MockAdapter instead of crashing the request.
"""
from __future__ import annotations
import logging
from app.adapters.base import AdapterError, ProviderAdapter
from app.adapters.mock_adapter import MockAdapter
logger = logging.getLogger("spacebound.adapters")
_BUILDERS = {
    "openai": lambda: __import__(
        "app.adapters.openai_adapter", fromlist=["OpenAIAdapter"]
    ).OpenAIAdapter(),
    "anthropic": lambda: __import__(
        "app.adapters.anthropic_adapter", fromlist=["AnthropicAdapter"]
    ).AnthropicAdapter(),
    "gemini": lambda: __import__(
        "app.adapters.gemini_adapter", fromlist=["GeminiAdapter"]
    ).GeminiAdapter(),
    "mock": lambda: MockAdapter(),
}
_cache: dict[str, ProviderAdapter] = {}
async def get_adapter(name: str, *, verify_health: bool = False) -> ProviderAdapter:
    """Build (or reuse) the named adapter. Falls back to mock on any
    construction failure -- this is what makes `provider: openai` a safe
    default even when OPENAI_API_KEY isn't set on this machine.
    """
    name = (name or "mock").lower()
    if name in _cache:
        adapter = _cache[name]
    else:
        builder = _BUILDERS.get(name)
        if builder is None:
            logger.warning("unknown provider '%s', falling back to mock", name)
            adapter = MockAdapter()
        else:
            try:
                adapter = builder()
            except AdapterError as e:
                logger.warning("provider '%s' unavailable (%s), falling back to mock", name, e)
                adapter = MockAdapter()
        _cache[name] = adapter
    if verify_health and adapter.name != "mock":
        ok = await adapter.health_check()
        if not ok:
            logger.warning("provider '%s' failed health check, falling back to mock", name)
            return MockAdapter()
    return adapter
def available_providers() -> list[str]:
    return list(_BUILDERS.keys())
def reset_cache() -> None:
    """Test hook -- clears cached adapter instances between test cases."""
    _cache.clear()
