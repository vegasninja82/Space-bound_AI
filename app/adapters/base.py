"""
Every provider adapter implements this interface. The engine never talks
to OpenAI/Anthropic/Gemini/mock directly -- it only talks to this contract,
which is what makes the registry's real/mock fallback possible.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator


class ProviderAdapter(ABC):
    name: str = "base"

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Return a single completed response."""
        raise NotImplementedError

    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Yield response chunks as they arrive."""
        raise NotImplementedError
        yield ""  # pragma: no cover - makes this an async generator

    @abstractmethod
    async def health_check(self) -> bool:
        """Cheap call to confirm the provider is reachable and configured."""
        raise NotImplementedError

    def token_usage(self) -> dict[str, int]:
        """Usage from the most recent generate()/stream() call."""
        return getattr(self, "_last_usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})


class AdapterError(RuntimeError):
    """Raised when a real provider can't be constructed or reached."""
