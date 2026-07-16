class BaselineBuilder:
    def build(self, request_text):
        return {"request": request_text, "meta": {"now": __import__('time').time()}}
