#!/usr/bin/env python3
import argparse, asyncio, json, os
from app.config import Config
from app.engine import Engine
from app.adapters.registry import AdapterRegistry
from util.logger import Logger

logger = Logger()

def banner(provider, tracks, scheduler_conf, validator_ver):
    print("SPACE_BOUND_AI ENGINE v1.0")
    print(f"Active provider: {provider}")
    print(f"Tracks: {', '.join(tracks)}")
    print(f"Scheduler: {scheduler_conf}")
    print(f"Validator: {validator_ver}")
    print("Heartbeat:", end=" ")

async def run_demo(provider):
    cfg = Config()
    registry = AdapterRegistry(cfg)
    adapter = registry.get(provider)
    engine = Engine(config=cfg, adapter=adapter, logger=logger)
    result = await engine.run("Demo request to verify heartbeat now")
    print(json.dumps(result, indent=2))
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default=None)
    args = parser.parse_args()
    cfg = Config()
    provider = args.provider or cfg.base.get("provider", "mock")
    banner(provider, list(cfg.tracks.keys()), cfg.scheduler, "v1.0")
    # short heartbeat
    for i in range(3):
        print(".", end="", flush=True)
        import time
        time.sleep(0.2)
    print()
    # run engine
    result = asyncio.run(run_demo(provider))
    # append metric to metrics.jsonl
    mf = os.environ.get("METRICS_FILE", "metrics.jsonl")
    with open(mf, "a") as f:
        f.write(json.dumps({"time": __import__('time').time(), "result": {"validation": result.get("validation"), "timing": result.get("timing")}}) + "\n")

if __name__ == "__main__":
    main()
