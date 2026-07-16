#!/usr/bin/env python3
import os, sys, json, time, asyncio, argparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import Config
from app.engine import Engine
from app.adapters.registry import AdapterRegistry
from app.metrics import MetricsRecorder
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

WEB_DIR = os.path.join(os.path.dirname(__file__), "web", "dist")


class ChatRequest(BaseModel):
    prompt: str
    provider: str | None = None


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0"}


@app.get("/providers")
async def get_providers():
    return {
        "active": cfg.base.get("provider", "mock"),
        "available": ["mock", "openai", "anthropic", "gemini"],
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
        "providers": ["mock", "openai", "anthropic", "gemini"],
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")
    provider = req.provider or cfg.base.get("provider", "mock")
    adapter = registry.get(provider)
    engine = Engine(config=cfg, adapter=adapter, logger=logger)
    result = await engine.run(req.prompt)
    return result


@app.get("/metrics")
async def get_metrics():
    rows = metrics_recorder.db.query(
        "SELECT id, ts, payload FROM metrics ORDER BY id DESC LIMIT 50"
    )
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


def run_cli():
    def banner(provider, tracks, scheduler_conf):
        print("SPACE_BOUND_AI ENGINE v1.0")
        print(f"Active provider: {provider}")
        print(f"Tracks: {', '.join(tracks)}")
        print(f"Scheduler: {scheduler_conf}")
        print("Heartbeat:", end=" ")

    async def run_demo(provider):
        registry = AdapterRegistry(cfg)
        adapter = registry.get(provider)
        engine = Engine(config=cfg, adapter=adapter, logger=logger)
        result = await engine.run("Demo request to verify heartbeat now")
        print(json.dumps(result, indent=2))
        return result

    provider = cfg.base.get("provider", "mock")
    banner(provider, list(cfg.tracks.keys()), cfg.scheduler)
    for i in range(3):
        print(".", end="", flush=True)
        time.sleep(0.2)
    print()
    result = asyncio.run(run_demo(provider))
    mf = os.environ.get("METRICS_FILE", "metrics.jsonl")
    with open(mf, "a") as f:
        f.write(json.dumps({"time": time.time(), "result": {"validation": result.get("validation"), "timing": result.get("timing")}}) + "\n")


def main():
    parser = argparse.ArgumentParser(description="SPACE_BOUND_AI")
    parser.add_argument("command", nargs="?", default="server", choices=["server", "demo"])
    parser.add_argument("--provider", default=None)
    args, extra = parser.parse_known_args()
    if args.command == "demo":
        run_cli()
    else:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


if __name__ == "__main__":
    main()
