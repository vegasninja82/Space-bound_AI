from app.adapters.base import AdapterBase
class OpenAIAdapter(AdapterBase):
    def __init__(self):
        # In MVP we don't call external services without keys; treat as unavailable
        pass
    def generate(self, prompt, **kwargs):
        raise RuntimeError("OpenAIAdapter not configured in demo mode")
    def health_check(self):
        return False
