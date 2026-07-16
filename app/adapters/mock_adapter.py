from app.adapters.base import AdapterBase

class MockAdapter(AdapterBase):
    def generate(self, prompt, **kwargs):
        return f"MOCK_ANSWER: deterministic answer for: {prompt}"
    def stream(self, prompt, **kwargs):
        for i in range(3):
            yield f"MOCK_CHUNK_{i} for {prompt}"
    def health_check(self):
        return True
    def token_usage(self):
        return {"prompt_tokens": 1, "completion_tokens": 1}
