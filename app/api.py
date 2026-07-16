import os, asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.config import Config
from app.engine import Engine
from app.adapters.registry import AdapterRegistry
from app.metrics import MetricsRecorder
from app.scheduler import Scheduler
from util.logger import Logger

logger = Logger()
cfg = Config()
registry = AdapterRegistry(cfg)
metrics_recorder = MetricsRecorder()

app = FastAPI(title="SPACE_BOUND_AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web", "dist")


class RunRequest(BaseModel):
    prompt: str
    provider: str | None = None


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0"}


@app.get("/api/config")
async def get_config():
    return {
        "provider": cfg.base.get("provider", "mock"),
        "tracks": list(cfg.tracks.keys()),
        "scheduler": cfg.scheduler,
        "providers": ["mock", "openai", "anthropic", "gemini"],
    }


@app.get("/api/tracks")
async def get_tracks():
    return {"tracks": cfg.tracks}


@app.post("/api/run")
async def run_engine(req: RunRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")
    provider = req.provider or cfg.base.get("provider", "mock")
    adapter = registry.get(provider)
    engine = Engine(config=cfg, adapter=adapter, logger=logger)
    result = await engine.run(req.prompt)
    return result


@app.get("/api/metrics")
async def get_metrics():
    rows = metrics_recorder.db.query(
        "SELECT id, ts, payload FROM metrics ORDER BY id DESC LIMIT 50"
    )
    import json
    return [
        {"id": r[0], "ts": r[1], "data": json.loads(r[2])}
        for r in rows
    ]


if os.path.isdir(WEB_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(WEB_DIR, "assets")), name="assets")

    @app.get("/{full_path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(WEB_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(WEB_DIR, "index.html"))
