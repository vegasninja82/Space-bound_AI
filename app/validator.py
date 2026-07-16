class Validator:
    def validate(self, merged):
        # simple deterministic validator
        return {"pass": True, "confidence": 93, "drift": 2, "notes": ["mock validator"]}
