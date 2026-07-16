import asyncio, time
from app.baseline import BaselineBuilder
from app.scheduler import Scheduler
from app.merge import MergeEngine
from app.validator import Validator
from app.metrics import MetricsRecorder

class Engine:
    def __init__(self, config, adapter, logger):
        self.config = config
        self.adapter = adapter
        self.logger = logger
        self.baseline = BaselineBuilder()
        self.scheduler = Scheduler(config)
        self.merge = MergeEngine()
        self.validator = Validator()
        self.metrics = MetricsRecorder()

    async def run_track(self, track_name, ctx):
        # adapter.generate is synchronous in MockAdapter for simplicity
        answer = self.adapter.generate(f"{track_name}:{ctx['request']}")
        return {"track": track_name, "answer": answer}

    async def run(self, request_text):
        start = time.time()
        ctx = self.baseline.build(request_text)
        tracks = list(self.config.tracks.keys())
        tasks = [self.run_track(t, ctx) for t in tracks]
        results = await asyncio.gather(*tasks)
        merged = self.merge.merge(results)
        validation = self.validator.validate(merged)
        total_ms = int((time.time()-start)*1000)
        try:
            self.metrics.record({"validation": validation, "timing": {"total_ms": total_ms}})
        except Exception:
            pass
        return {"answer": merged["answer"], "validation": validation, "timing": {"total_ms": total_ms}}
