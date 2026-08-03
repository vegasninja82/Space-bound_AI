"""
Real validation engine.
Honest framing up front: without ground truth, no automated check can
tell you a response is *factually correct*. What this module actually
measures is response *stability* and a handful of surface-level red
flags -- real signals, but not a correctness guarantee. Don't let the
confidence number imply more than that in the UI copy.
Two real techniques, both stdlib-only (no new dependencies):
1. Self-consistency drift: generate a second, independent sample for the
   same prompt and diff it against the first with difflib. Two runs that
   agree closely -> the model is stable on this prompt -> lower drift.
   Two runs that diverge heavily -> lower confidence. This is the same
   idea behind sampling-based uncertainty estimation (e.g. SelfCheckGPT-
   style consistency checks), just without an embeddings dependency.
2. Heuristic signals: hedging language, response length relative to the
   prompt, and a coarse same-response contradiction check. These catch
   surface issues (the model visibly hedging, or answering both "yes"
   and "no") -- they do not catch subtle factual errors.
"""
from __future__ import annotations
import difflib
import re
from app.adapters.base import ProviderAdapter
from app.models import ValidationResult
_HEDGE_PATTERNS = [
    r"\bi'?m not sure\b", r"\bi don'?t know\b", r"\bmight be\b",
    r"\bpossibly\b", r"\bunclear\b", r"\bcannot verify\b",
    r"\bit'?s hard to say\b", r"\bmay or may not\b",
]
_HEDGE_RE = re.compile("|".join(_HEDGE_PATTERNS), re.IGNORECASE)
# Deliberately coarse: this catches only the loudest self-contradictions
# (both an affirmative and negative headline claim in the same response),
# not subtle logical inconsistency. Treat it as a smoke detector, not a
# fact-checker.
_YES_RE = re.compile(r"\byes\b", re.IGNORECASE)
_NO_RE = re.compile(r"\bno\b", re.IGNORECASE)
def _similarity(a: str, b: str) -> float:
    """0.0 (nothing alike) to 1.0 (identical)."""
    return difflib.SequenceMatcher(None, a, b).ratio()
def _hedge_penalty(text: str) -> tuple[int, list[str]]:
    hits = _HEDGE_RE.findall(text)
    if not hits:
        return 0, []
    penalty = min(30, 10 * len(hits))
    return penalty, [f"hedging language detected ({len(hits)} instance(s))"]
def _length_penalty(prompt: str, text: str) -> tuple[int, list[str]]:
    # Very rough proxy: a prompt with several distinct asks (question
    # marks, "and", numbered items) should produce a response with
    # comparable structure. This won't catch a subtly incomplete answer,
    # but it does catch a one-line reply to a multi-part question.
    asks = prompt.count("?") + prompt.count("\n-") + prompt.count("\n1.")
    asks = max(1, asks)
    sentences = max(1, text.count(". ") + text.count(".\n") + 1)
    if asks > 1 and sentences < asks:
        return 15, [f"response has {sentences} sentence(s) for an estimated {asks} distinct ask(s)"]
    return 0, []
def _contradiction_penalty(text: str) -> tuple[int, list[str]]:
    if _YES_RE.search(text) and _NO_RE.search(text):
        return 20, ["response contains both an affirmative and a negative headline claim"]
    return 0, []
async def validate(
    prompt: str,
    direct_text: str,
    adapter: ProviderAdapter,
    *,
    confidence_threshold: int = 60,
    drift_threshold: float = 40.0,
    second_sample: bool = True,
) -> ValidationResult:
    notes: list[str] = []
    signals: dict = {}
    drift = 0.0
    if second_sample:
        second_text = await adapter.generate(prompt, framing="independent re-generation for consistency check")
        sim = _similarity(direct_text, second_text)
        drift = round((1.0 - sim) * 100, 1)
        signals["second_sample_similarity"] = round(sim, 3)
        if drift > drift_threshold:
            notes.append(f"drift {drift}% exceeds threshold {drift_threshold}% -- two independent samples disagreed")
    confidence = 100
    for penalty_fn in (_hedge_penalty, _contradiction_penalty):
        penalty, msgs = penalty_fn(direct_text)
        confidence -= penalty
        notes.extend(msgs)
    len_penalty, len_notes = _length_penalty(prompt, direct_text)
    confidence -= len_penalty
    notes.extend(len_notes)
    # Drift itself feeds back into confidence -- an unstable answer is,
    # by definition, one you should trust less.
    confidence -= int(drift * 0.3)
    confidence = max(0, min(100, confidence))
    signals["drift_penalty_applied"] = int(drift * 0.3)
    passed = confidence >= confidence_threshold and drift <= drift_threshold
    return ValidationResult(
        confidence=confidence,
        drift=drift,
        passed=passed,
        signals=signals,
        notes=notes,
    )
