"""Dataclasses shared across app modules."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    confidence: int
    drift: float
    passed: bool
    signals: dict
    notes: list[str]


@dataclass
class PerspectiveResult:
    name: str
    summary: str
    flags: list[str]
