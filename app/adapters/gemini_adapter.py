"""
Real Gemini adapter, written against `google-generativeai`
(`import google.generativeai as genai`).

Flagging this one specifically: Google has shipped more than one Python
SDK shape for Gemini over the last couple of years (google-generativeai
vs. the newer google-genai package), and the method names moved between
them. If `pip install -r requirements.txt` pulls a version whose API
doesn't match what's below, this is the file to check first -- confirm
against whichever SDK version is actually pinned before trusting it.
"""
from __future__ import annotations

import os
import time
from typing import AsyncIterator

from app.adapters.base import AdapterError, ProviderAdapter

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None  # type: ignore


class GeminiAdapter(ProviderAdapter):
    name = "gemini"

    def __init__(self, model: str = "gemini-1.5-flash"):
        if genai is None:
            raise AdapterError("google-generativeai package is not installed")
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise AdapterError("GEMINI_API_KEY is not set")
        genai.configure(api_key=api_key)
        self._model_name = model
        self._last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _model(self, framing: str = ""):
        return genai.GenerativeModel(
            self._model_name,
            system_instruction=framing or None,
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        framing = kwargs.get("framing", kwargs.get("system_prompt", ""))
        model = self._model(framing)
        response = await model.generate_content_async(prompt)
        usage = getattr(response, "usage_metadata", None)
        if usage:
            self._last_usage = {
                "prompt_tokens": usage.prompt_token_count,
                "completion_tokens": usage.candidates_token_count,
                "total_tokens": usage.total_token_count,
            }
        return response.text

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        framing = kwargs.get("framing", kwargs.get("system_prompt", ""))
        model = self._model(framing)
        response = await model.generate_content_async(prompt, stream=True)
        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def health_check(self) -> bool:
        try:
            start = time.monotonic()
            model = self._model()
            await model.generate_content_async("ping")
            return time.monotonic() - start < 30
        except Exception:
            return False
