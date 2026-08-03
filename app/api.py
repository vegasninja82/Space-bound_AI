"""
FastAPI application layer. All HTTP routes live here; main.py just
imports `app` from this module and runs uvicorn.
"""
from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.adapters.registry import available_providers, get_adapter
from app.config import Config
from app.engine import Engine
from app.perspective_engine import available_perspectives
from app.storage import MetricsRecorder
from util.logger import Logger

logger = Logger()
cfg = Config()
metrics_recorder = MetricsRecorder()

app = FastAPI(title="SPACE_BOUND_AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "dist")


class ChatRequest(BaseModel):
    prompt: str
    provider: str | None = None
    perspectives: list[str] | None = None


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0"}


@app.get("/providers")
async def get_providers():
    return {
        "active": cfg.base.get("provider", "mock"),
        "available": available_providers(),
    }


@app.get("/perspectives")
async def get_perspectives():
    return {
        "available": available_perspectives(),
        "mode": cfg.perspectives.get("mode", "subset"),
        "subset": cfg.perspectives.get("subset", []),
    }


@app.get("/tracks")
async def get_tracks():
    return {"tracks": list(cfg.tracks.keys())}


@app.get("/config")
async def get_config():
    return {
        "provider": cfg.base.get("provider", "mock"),
        "tracks": list(cfg.tracks.keys()),
        "scheduler": cfg.scheduler,
        "providers": available_providers(),
        "perspectives": cfg.perspectives,
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")
    provider = req.provider or cfg.base.get("provider", "mock")
    adapter = await get_adapter(provider)
    engine = Engine(config=cfg, adapter=adapter, logger=logger)
    result = await engine.run(req.prompt)
    return result


@app.get("/metrics")
async def get_metrics():
    return metrics_recorder.query_recent(50)


if os.path.isdir(WEB_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(WEB_DIR, "assets")), name="assets")

    @app.get("/{full_path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(WEB_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(WEB_DIR, "index.html"))
