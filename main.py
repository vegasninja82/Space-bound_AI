#!/usr/bin/env python3
"""Entry point: runs the FastAPI server (via uvicorn) or a CLI demo."""
import os
import sys
import json
import time
import asyncio
import argparse

from app.api import app, cfg, get_adapter
from app.engine import Engine
from util.logger import Logger


def run_cli():
    logger = Logger()

    def banner(provider, tracks, scheduler_conf):
        print("SPACE_BOUND_AI ENGINE v1.0")
        print(f"Active provider: {provider}")
        print(f"Tracks: {', '.join(tracks)}")
        print(f"Scheduler: {scheduler_conf}")
        print("Heartbeat:", end=" ")

    async def run_demo(provider):
        adapter = await get_adapter(provider)
        engine = Engine(config=cfg, adapter=adapter, logger=logger)
        result = await engine.run("Demo request to verify heartbeat now")
        print(json.dumps(result, indent=2))
        return result

    provider = cfg.base.get("provider", "mock")
    banner(provider, list(cfg.tracks.keys()), cfg.scheduler)
    for _ in range(3):
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
    args, _ = parser.parse_known_args()
    if args.command == "demo":
        run_cli()
    else:
        import uvicorn
        uvicorn.run("app.api:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))


if __name__ == "__main__":
    main()
