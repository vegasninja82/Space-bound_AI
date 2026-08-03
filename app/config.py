"""
Thin wrapper around config_loader.load_config that exposes the same
attribute-style access the rest of the app expects (config.base,
config.tracks, config.scheduler, config.perspectives, config.validation).
"""
from __future__ import annotations

from app.config_loader import load_config


class Config:
    def __init__(self):
        data = load_config()
        self.base = data
        self.tracks = data.get("tracks", {})
        self.scheduler = data.get("scheduler", {"type": "simple"})
        self.perspectives = data.get("perspectives", {"mode": "subset", "subset": []})
        self.validation = data.get("validation", {"confidence_threshold": 60, "drift_threshold": 40.0, "second_sample": True})
        self.merge = data.get("merge", {"use_llm_synthesis": False, "append_perspective_flags": True})
        self.reality_feed = data.get("reality_feed", {"ttl_ms": 100, "timeout_ms": 50})
        self.storage = data.get("storage", {"path": "storage/metrics.db"})
