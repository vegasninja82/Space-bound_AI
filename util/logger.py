import json, sys, time

class Logger:
    def _emit(self, level, msg, **kwargs):
        rec = {"ts": time.time(), "level": level, "msg": msg}
        rec.update(kwargs)
        print(json.dumps(rec), file=sys.stdout, flush=True)
    def info(self, msg, **k): self._emit("INFO", msg, **k)
    def warn(self, msg, **k): self._emit("WARN", msg, **k)
    def error(self, msg, **k): self._emit("ERROR", msg, **k)
    def debug(self, msg, **k): self._emit("DEBUG", msg, **k)
