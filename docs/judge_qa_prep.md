# judge QA prep

What is SPACE_BOUND_AI?
- A provider-independent multi-track reasoning engine.

Why multiple tracks?
- Redundancy and complementary reasoning strategies to reduce hallucination.

Why not one model?
- Ensemble reduces single-model failure modes.

How does provider independence work?
- Adapter pattern isolates provider-specific code.

What does validation do?
- Runs deterministic checks producing pass/confidence/drift.

How does scheduling work?
- Simple parallel scheduler in MVP.

What's next?
- Real adapters, tests, dashboard.
