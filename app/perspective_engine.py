"""
Real 12-perspective analysis.
Cost note, stated plainly: every perspective is a real LLM call. Running
all 12 means 12 extra round trips on top of the direct response and the
validation re-sample -- real latency, real token spend, per request. The
"mode: subset" default in config/base.yml exists because most use cases
don't need all twelve every time. Set perspectives.mode to "all" (or pass
`perspectives` explicitly in the request) once you've decided the cost is
worth it for your use case.
"""
from __future__ import annotations
import asyncio
from app.adapters.base import ProviderAdapter
from app.models import PerspectiveResult
# Each lens gets a distinct system prompt so the adapter actually produces
# different text per perspective, not the same answer with a new label.
_LENSES: dict[str, str] = {
    "engineering": "Analyze this from an engineering perspective: feasibility, performance, scalability.",
    "scientific": "Analyze this from a scientific perspective: methodology, evidence, accuracy.",
    "business": "Analyze this from a business perspective: ROI, market fit, viability.",
    "economic": "Analyze this from an economic perspective: cost-benefit, financial impact.",
    "security": "Analyze this from a security perspective: vulnerabilities, threat model, protection.",
    "legal": "Analyze this from a legal perspective: compliance, liability, IP.",
    "ethics": "Analyze this from an ethics perspective: bias, fairness, social impact.",
    "ux": "Analyze this from a user experience perspective: usability, accessibility, satisfaction.",
    "operations": "Analyze this from an operations perspective: implementation, maintenance, support.",
    "education": "Analyze this from an education perspective: learning curve, documentation, knowledge transfer.",
    "risk": "Analyze this from a risk-analysis perspective: failure modes, contingency, mitigation.",
    "design": "Analyze this from a system-design perspective: architecture, reliability, fault tolerance.",
}
_FLAG_KEYWORDS = {
    "risk": ["risk", "failure", "vulnerab", "expensive", "costly", "unclear", "fragile"],
    "cost": ["expensive", "costly", "budget", "overhead"],
}
def _flags_for(text: str) -> list[str]:
    lowered = text.lower()
    return [flag for flag, kws in _FLAG_KEYWORDS.items() if any(kw in lowered for kw in kws)]
async def _run_one(name: str, prompt: str, adapter: ProviderAdapter) -> PerspectiveResult:
    framing = _LENSES[name]
    text = await adapter.generate(prompt, framing=framing)
    return PerspectiveResult(name=name, summary=text, flags=_flags_for(text))
async def analyze(
    prompt: str,
    adapter: ProviderAdapter,
    *,
    mode: str = "subset",
    subset: list[str] | None = None,
    requested: list[str] | None = None,
) -> list[PerspectiveResult]:
    """Run the configured perspectives in parallel.
    Priority: an explicit `requested` list (from the API request) wins;
    otherwise fall back to config (`mode` + `subset`).
    """
    if requested:
        names = [n for n in requested if n in _LENSES]
    elif mode == "all":
        names = list(_LENSES.keys())
    else:
        names = [n for n in (subset or []) if n in _LENSES]
    if not names:
        return []
    results = await asyncio.gather(*(_run_one(n, prompt, adapter) for n in names))
    return list(results)
def available_perspectives() -> list[str]:
    return list(_LENSES.keys())
