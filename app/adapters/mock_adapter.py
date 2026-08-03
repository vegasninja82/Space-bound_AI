"""
The mock adapter is not a placeholder -- it's a real, deterministic
stand-in used by tests and local runs with no API keys. Determinism
matters: the validator's drift score and the perspective engine's
distinct-output checks both need repeatable behavior to be testable.
"""
from __future__ import annotations

import asyncio
import hashlib
from typing import AsyncIterator

from app.adapters.base import ProviderAdapter

# A small bank of sentence templates. Which one gets used is picked
# deterministically from a hash of (prompt + framing), so:
#   - the same prompt+framing always returns the same text (testable)
#   - different framings (perspectives) return genuinely different text
#     (so perspective analysis isn't just running the same string 12x)
_TEMPLATES = [
    "Based on the request, the core answer centers on {topic}. "
    "The key mechanism is straightforward once broken into steps.",
    "Looking at {topic}, the main consideration is trade-offs between "
    "simplicity and completeness. A direct approach handles most cases.",
    "{topic} resolves to a small set of concrete actions. Start with the "
    "simplest version, then iterate once the basic case is confirmed.",
    "The relevant factors for {topic} are scope, cost, and reliability. "
    "A minimal implementation addresses the immediate need first.",
]


def _topic_from(prompt: str) -> str:
    words = [w.strip(".,!?") for w in prompt.split() if len(w) > 3]
    return " ".join(words[:4]) if words else "this request"


class MockAdapter(ProviderAdapter):
    name = "mock"

    def __init__(self, latency_s: float = 0.01):
        self._latency_s = latency_s
        self._last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _deterministic_text(self, prompt: str, framing: str = "") -> str:
        key = f"{framing}::{prompt}".encode()
        idx = int(hashlib.sha256(key).hexdigest(), 16) % len(_TEMPLATES)
        text = _TEMPLATES[idx].format(topic=_topic_from(prompt))
        if framing:
            text = f"[{framing}] {text}"
        return text

    async def generate(self, prompt: str, **kwargs) -> str:
        await asyncio.sleep(self._latency_s)
        framing = kwargs.get("framing", kwargs.get("system_prompt", ""))
        text = self._deterministic_text(prompt, framing)
        prompt_tokens = max(1, len(prompt.split()))
        completion_tokens = max(1, len(text.split()))
        self._last_usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }
        return text

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        text = await self.generate(prompt, **kwargs)
        for word in text.split(" "):
            await asyncio.sleep(0)
            yield word + " "

    async def health_check(self) -> bool:
        return True
