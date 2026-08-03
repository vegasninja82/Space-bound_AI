from app.adapters.base import AdapterBase
import os

class GeminiAdapter(AdapterBase):
    """Google Gemini adapter for provider integration.
    
    Requires GEMINI_API_KEY environment variable.
    """
    
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.model = "gemini-2.0-flash"
    
    def generate(self, prompt, **kwargs):
        """Generate response using Google Gemini API.
        
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
                "Gemini API key not configured. "
                "Set GEMINI_API_KEY environment variable."
            )
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(kwargs.get("model", self.model))
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get("max_tokens", 500),
                    temperature=kwargs.get("temperature", 0.7)
                )
            )
            
            return response.text
        except ImportError:
            raise RuntimeError("google-generativeai package not installed. Run: pip install google-generativeai")
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {str(e)}")
    
    def stream(self, prompt, **kwargs):
        """Stream response from Gemini API.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
        
        Yields:
            Response chunks
        """
        if not self.api_key:
            raise RuntimeError("Gemini API key not configured")
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(kwargs.get("model", self.model))
            
            response = model.generate_content(
                prompt,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get("max_tokens", 500),
                    temperature=kwargs.get("temperature", 0.7)
                )
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"Stream error: {str(e)}"
    
    def health_check(self):
        """Check if Gemini API is accessible.
        
        Returns:
            True if API key is configured and API is accessible
        """
        if not self.api_key:
            return False
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            # Make a minimal request to verify API access
            response = model.generate_content("ping")
            return len(response.text) > 0
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