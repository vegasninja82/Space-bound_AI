import asyncio
import time
from dataclasses import dataclass, field

import aiohttp


@dataclass
class Actuality:
    data: dict = field(default_factory=dict)
    timestamp: float = 0.0


class RealityFeed:
    SAFE_DEFAULT = {
        "green_light": False,
        "cross_traffic": "UNKNOWN",
        "system_nominal": False,
    }

    CACHE_TTL_MS = 100.0
    DEADLINE_MS = 50.0

    def __init__(self, endpoint: str = "http://localhost:8081/sensor"):
        self._endpoint = endpoint
        self._cache: Actuality | None = None
        self._session: aiohttp.ClientSession | None = None
        self._client = self

    def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def get(self, url: str, **kwargs):
        session = self._ensure_session()
        async with session.get(url, **kwargs) as resp:
            return resp

    async def warmup(self) -> None:
        try:
            await self._fetch_with_deadline()
        except Exception:
            pass

    async def _fetch_with_deadline(self) -> dict:
        try:
            raw = await asyncio.wait_for(
                self._client.get(self._endpoint),
                timeout=self.DEADLINE_MS / 1000.0,
            )
            data = await raw.json()
            self._cache = Actuality(data=data, timestamp=time.time() * 1000)
            return data
        except asyncio.TimeoutError:
            self._cache = Actuality(
                data=dict(self.SAFE_DEFAULT),
                timestamp=time.time() * 1000,
            )
            return self._cache.data
        except Exception:
            self._cache = Actuality(
                data=dict(self.SAFE_DEFAULT),
                timestamp=time.time() * 1000,
            )
            return self._cache.data

    async def get_live_actuality(self) -> dict:
        now_ms = time.time() * 1000
        if self._cache is not None:
            age = now_ms - self._cache.timestamp
            if age < self.CACHE_TTL_MS:
                return dict(self._cache.data)
        return await self._fetch_with_deadline()

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
