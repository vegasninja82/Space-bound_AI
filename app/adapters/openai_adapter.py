"""
Real OpenAI adapter. Needs OPENAI_API_KEY and the `openai` package
(both already in requirements.txt). Can't be exercised against the live
API from this sandbox (no network here) -- test it locally with a real
key before you trust it in the pipeline.
"""
from __future__ import annotations

import os
import time
from typing import AsyncIterator

from app.adapters.base import AdapterError, ProviderAdapter

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore


class OpenAIAdapter(ProviderAdapter):
    name = "openai"

    def __init__(self, model: str = "gpt-4o-mini"):
        if AsyncOpenAI is None:
            raise AdapterError("openai package is not installed")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise AdapterError("OPENAI_API_KEY is not set")
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _messages(self, prompt: str, framing: str = "") -> list[dict]:
        msgs = []
        if framing:
            msgs.append({"role": "system", "content": framing})
        msgs.append({"role": "user", "content": prompt})
        return msgs

    async def generate(self, prompt: str, **kwargs) -> str:
        framing = kwargs.get("framing", kwargs.get("system_prompt", ""))
        response = await self._client.chat.completions.create(
            model=kwargs.get("model", self._model),
            messages=self._messages(prompt, framing),
        )
        if response.usage:
            self._last_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        return response.choices[0].message.content or ""

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        framing = kwargs.get("framing", kwargs.get("system_prompt", ""))
        stream = await self._client.chat.completions.create(
            model=kwargs.get("model", self._model),
            messages=self._messages(prompt, framing),
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def health_check(self) -> bool:
        try:
            start = time.monotonic()
            await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
            )
            return time.monotonic() - start < 30
        except Exception:
            return False
