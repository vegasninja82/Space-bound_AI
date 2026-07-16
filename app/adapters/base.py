class AdapterBase:
    def generate(self, prompt, **kwargs):
        raise NotImplementedError()
    def stream(self, prompt, **kwargs):
        # should be async generator in full impl; here simple generator
        yield ""
    def health_check(self):
        return False
    def token_usage(self):
        return {"prompt":0, "completion":0}
