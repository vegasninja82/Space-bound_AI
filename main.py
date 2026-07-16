#!/usr/bin/env python3
import argparse, sys

def run_cli():
    import asyncio, json, os, time
    from app.config import Config
    from app.engine import Engine
    from app.adapters.registry import AdapterRegistry
    from util.logger import Logger

    logger = Logger()

    def banner(provider, tracks, scheduler_conf):
        print("SPACE_BOUND_AI ENGINE v1.0")
        print(f"Active provider: {provider}")
        print(f"Tracks: {', '.join(tracks)}")
        print(f"Scheduler: {scheduler_conf}")
        print("Heartbeat:", end=" ")

    async def run_demo(provider):
        cfg = Config()
        registry = AdapterRegistry(cfg)
        adapter = registry.get(provider)
        engine = Engine(config=cfg, adapter=adapter, logger=logger)
        result = await engine.run("Demo request to verify heartbeat now")
        print(json.dumps(result, indent=2))
        return result

    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default=None)
    args = parser.parse_args()
    cfg = Config()
    provider = args.provider or cfg.base.get("provider", "mock")
    banner(provider, list(cfg.tracks.keys()), cfg.scheduler)
    for i in range(3):
        print(".", end="", flush=True)
        time.sleep(0.2)
    print()
    result = asyncio.run(run_demo(provider))
    mf = os.environ.get("METRICS_FILE", "metrics.jsonl")
    with open(mf, "a") as f:
        f.write(json.dumps({"time": time.time(), "result": {"validation": result.get("validation"), "timing": result.get("timing")}}) + "\n")

def run_server():
    import uvicorn
    uvicorn.run("app.api:app", host="0.0.0.0", port=int(__import__("os").environ.get("PORT", 8000)))

def main():
    parser = argparse.ArgumentParser(description="SPACE_BOUND_AI")
    parser.add_argument("command", nargs="?", default="server", choices=["server", "demo"])
    parser.add_argument("--provider", default=None)
    args, extra = parser.parse_known_args()
    if args.command == "demo":
        sys.argv = [sys.argv[0]] + (["--provider", args.provider] if args.provider else [])
        run_cli()
    else:
        run_server()

if __name__ == "__main__":
    main()
