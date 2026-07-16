from app.adapters.base import AdapterBase
class AnthropicAdapter(AdapterBase):
    def __init__(self):
        pass
    def generate(self, prompt, **kwargs):
        raise RuntimeError("AnthropicAdapter not configured in demo mode")
    def health_check(self):
        return False
