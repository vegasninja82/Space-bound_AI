import time, asyncio
from app.config import Config
from app.adapters.registry import AdapterRegistry
from app.engine import Engine
from util.logger import Logger

async def benchmark(provider='mock'):
    cfg = Config()
    adapter = AdapterRegistry(cfg).get(provider)
    engine = Engine(cfg, adapter, Logger())
    start = time.time()
    await engine.run("benchmark request")
    total_ms = (time.time()-start)*1000
    print(f"total_latency_ms={int(total_ms)}")
    return int(total_ms)

if __name__ == '__main__':
    import sys
    provider = 'mock'
    if len(sys.argv) > 1:
        provider = sys.argv[1]
    ms = asyncio.run(benchmark(provider))
    if ms > 4000:
        print("WARN: latency > 4000ms")
    else:
        print("OK: latency under threshold")
