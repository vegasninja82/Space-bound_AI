from app.adapters.mock_adapter import MockAdapter
from app.adapters.openai_adapter import OpenAIAdapter
from app.adapters.anthropic_adapter import AnthropicAdapter
from app.adapters.gemini_adapter import GeminiAdapter

class AdapterRegistry:
    def __init__(self, config=None):
        self.config = config
        self._map = {
            'mock': MockAdapter,
            'openai': OpenAIAdapter,
            'anthropic': AnthropicAdapter,
            'gemini': GeminiAdapter,
        }
    def get(self, name):
        cls = self._map.get(name, MockAdapter)
        try:
            inst = cls()
            if not inst.health_check():
                # fallback
                return MockAdapter()
            return inst
        except Exception:
            return MockAdapter()
