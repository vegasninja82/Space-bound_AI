"""
Real Anthropic adapter. Needs ANTHROPIC_API_KEY and the `anthropic`
package. Same caveat as the OpenAI adapter: written correctly against
the documented SDK shape, but untested against the live API from this
sandbox since it has no network access.
"""
from __future__ import annotations

import os
import time
from typing import AsyncIterator

from app.adapters.base import AdapterError, ProviderAdapter

try:
    from anthropic import AsyncAnthropic
except ImportError:  # pragma: no cover
    AsyncAnthropic = None  # type: ignore


class AnthropicAdapter(ProviderAdapter):
    name = "anthropic"

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", max_tokens: int = 1024):
        if AsyncAnthropic is None:
            raise AdapterError("anthropic package is not installed")
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise AdapterError("ANTHROPIC_API_KEY is not set")
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens
        self._last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    async def generate(self, prompt: str, **kwargs) -> str:
        framing = kwargs.get("framing", kwargs.get("system_prompt", ""))
        response = await self._client.messages.create(
            model=kwargs.get("model", self._model),
            max_tokens=kwargs.get("max_tokens", self._max_tokens),
            system=framing or None,
            messages=[{"role": "user", "content": prompt}],
        )
        if response.usage:
            self._last_usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }
        return "".join(block.text for block in response.content if block.type == "text")

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        framing = kwargs.get("framing", kwargs.get("system_prompt", ""))
        async with self._client.messages.stream(
            model=kwargs.get("model", self._model),
            max_tokens=kwargs.get("max_tokens", self._max_tokens),
            system=framing or None,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def health_check(self) -> bool:
        try:
            start = time.monotonic()
            await self._client.messages.create(
                model=self._model,
                max_tokens=1,
                messages=[{"role": "user", "content": "ping"}],
            )
            return time.monotonic() - start < 30
        except Exception:
            return False
