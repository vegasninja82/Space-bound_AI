from app.adapters.base import AdapterBase
class GeminiAdapter(AdapterBase):
    def __init__(self):
        pass
    def generate(self, prompt, **kwargs):
        raise RuntimeError("GeminiAdapter not configured in demo mode")
    def health_check(self):
        return False
