from app.adapters.base import AdapterBase
import os

class OpenAIAdapter(AdapterBase):
    """OpenAI GPT adapter for provider integration.
    
    Requires OPENAI_API_KEY environment variable.
    """
    
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.model = "gpt-4o-mini"
        self.base_url = "https://api.openai.com/v1"
    
    def generate(self, prompt, **kwargs):
        """Generate response using OpenAI API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (model, temperature, etc.)
        
        Returns:
            Generated text response
        
        Raises:
            RuntimeError: If API key not configured
        """
        if not self.api_key:
            raise RuntimeError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable."
            )
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 500)
            )
            
            return response.choices[0].message.content
        except ImportError:
            raise RuntimeError("openai package not installed. Run: pip install openai")
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def stream(self, prompt, **kwargs):
        """Stream response from OpenAI API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
        
        Yields:
            Response chunks
        """
        if not self.api_key:
            raise RuntimeError("OpenAI API key not configured")
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            with client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 500),
                stream=True
            ) as response:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Stream error: {str(e)}"
    
    def health_check(self):
        """Check if OpenAI API is accessible.
        
        Returns:
            True if API key is configured and models are accessible
        """
        if not self.api_key:
            return False
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            # List models to verify API access
            client.models.list()
            return True
        except Exception:
            return False
    
    def token_usage(self):
        """Return token usage structure.
        
        Returns:
            Dict with prompt_tokens and completion_tokens
        """
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }