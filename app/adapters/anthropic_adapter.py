from app.adapters.base import AdapterBase
import os

class AnthropicAdapter(AdapterBase):
    """Anthropic Claude adapter for provider integration.
    
    Requires ANTHROPIC_API_KEY environment variable.
    """
    
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.model = "claude-3-5-sonnet-20241022"
    
    def generate(self, prompt, **kwargs):
        """Generate response using Anthropic API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (model, max_tokens, etc.)
        
        Returns:
            Generated text response
        
        Raises:
            RuntimeError: If API key not configured
        """
        if not self.api_key:
            raise RuntimeError(
                "Anthropic API key not configured. "
                "Set ANTHROPIC_API_KEY environment variable."
            )
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=kwargs.get("model", self.model),
                max_tokens=kwargs.get("max_tokens", 500),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
        except ImportError:
            raise RuntimeError("anthropic package not installed. Run: pip install anthropic")
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    def stream(self, prompt, **kwargs):
        """Stream response from Anthropic API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
        
        Yields:
            Response chunks
        """
        if not self.api_key:
            raise RuntimeError("Anthropic API key not configured")
        
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            with client.messages.stream(
                model=kwargs.get("model", self.model),
                max_tokens=kwargs.get("max_tokens", 500),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"Stream error: {str(e)}"
    
    def health_check(self):
        """Check if Anthropic API is accessible.
        
        Returns:
            True if API key is configured and API is accessible
        """
        if not self.api_key:
            return False
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            # Make a minimal request to verify API access
            response = client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "ping"}
                ]
            )
            return response.stop_reason == "end_turn"
        except Exception:
            return False
    
    def token_usage(self):
        """Return token usage structure.
        
        Returns:
            Dict with input_tokens and output_tokens
        """
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }