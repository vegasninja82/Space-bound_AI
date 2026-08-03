from app.adapters.mock_adapter import MockAdapter
from app.adapters.openai_adapter import OpenAIAdapter
from app.adapters.anthropic_adapter import AnthropicAdapter
from app.adapters.gemini_adapter import GeminiAdapter


class AdapterRegistry:
    """Registry for managing provider adapters.
    
    Maps provider names to adapter instances with fallback to mock adapter.
    """
    
    def __init__(self, config):
        self.config = config
        self.adapters = {
            "mock": MockAdapter(),
            "openai": OpenAIAdapter(),
            "anthropic": AnthropicAdapter(),
            "gemini": GeminiAdapter(),
        }
    
    def get(self, provider_name):
        """Get an adapter by provider name.
        
        Args:
            provider_name: Name of the provider (mock, openai, anthropic, gemini)
        
        Returns:
            Adapter instance. Falls back to MockAdapter if provider not found
            or if the requested adapter is not healthy (e.g., missing API key).
        """
        adapter = self.adapters.get(provider_name)
        
        if adapter is None:
            # Provider not in registry, use mock
            return self.adapters["mock"]
        
        # For non-mock adapters, check health and fallback if unavailable
        if provider_name != "mock":
            try:
                if not adapter.health_check():
                    # Adapter is not healthy (API key missing, service down, etc.)
                    # Fall back to mock with a note
                    return self.adapters["mock"]
            except Exception:
                # If health check raises, fall back to mock
                return self.adapters["mock"]
        
        return adapter