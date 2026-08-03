"""
Loads config/*.yml into one merged dict. Every key has a real default
baked in here, so a fresh checkout with no config/ directory still boots.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULTS: dict[str, Any] = {
    "provider": "mock",
    "logging": {"level": "INFO"},
    "enable_zero_hour_gate": False,
    "afterthought_window_ms": 3000,
    "tracks": {
        "direct": True,
        "validation": True,
        "perspective": True,
    },
    "perspectives": {
        # Running all 12 means 12 extra LLM calls on top of the direct
        # response. That's real latency and real API cost. Default to a
        # smaller, high-signal subset; set to "all" to run every lens.
        "mode": "subset",
        "subset": ["engineering", "security", "risk", "ux"],
        "all": [
            "engineering", "scientific", "business", "economic",
            "security", "legal", "ethics", "ux", "operations",
            "education", "risk", "design",
        ],
    },
    "validation": {
        "confidence_threshold": 60,
        "drift_threshold": 40.0,
        "second_sample": True,
    },
    "merge": {
        "use_llm_synthesis": False,
        "append_perspective_flags": True,
    },
    "reality_feed": {
        "ttl_ms": 100,
        "timeout_ms": 50,
    },
    "storage": {
        "path": "storage/metrics.db",
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_config(config_dir: str | Path = "config") -> dict[str, Any]:
    """Merge every config/*.yml over DEFAULTS. Missing files are skipped,
    not fatal -- a bad/missing YAML file should never take the service down.
    """
    cfg = dict(DEFAULTS)
    config_dir = Path(config_dir)
    for fname in ("base.yml", "tracks.yml", "scheduler.yml", "providers.yml", "dashboard.yml"):
        fpath = config_dir / fname
        if not fpath.exists():
            continue
        try:
            with open(fpath) as f:
                data = yaml.safe_load(f) or {}
            cfg = _deep_merge(cfg, data)
        except yaml.YAMLError as e:
            # Log-and-continue: one malformed config file shouldn't crash boot.
            print(f"[config] skipping {fpath}, failed to parse: {e}")
    # Env var override for provider, since that's the one people change most.
    if os.environ.get("SPACEBOUND_PROVIDER"):
        cfg["provider"] = os.environ["SPACEBOUND_PROVIDER"]
    return cfg
