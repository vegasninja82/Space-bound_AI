# SPACE_BOUND_AI — Architecture Overview

## System Summary

SPACE_BOUND_AI is a Python-based, provider-independent, multi-track AI reasoning orchestration engine. It coordinates multiple reasoning stages concurrently before producing a validated final output. A React/Vite TypeScript dashboard provides a web interface for interactive engine execution and metrics visualization.

---

## Backend: Python FastAPI

### Entry Point (`main.py`)

- **FastAPI** application with 6 REST endpoints: `/health`, `/providers`, `/tracks`, `/config`, `/chat`, `/metrics`
- CORS middleware enabled for cross-origin requests
- Serves the built frontend from `web/dist/` as static files when available
- CLI demo mode: `python main.py demo` runs a single pipeline request and writes metrics to JSONL
- Server mode: `python main.py` starts uvicorn on port 8000

### Multi-Track Reasoning Engine (`app/engine.py`)

The `Engine` class orchestrates the full pipeline:

1. **BaselineBuilder** (`app/baseline.py`) — Constructs the request context: `{"request": <text>, "meta": {"now": <timestamp>}}`
2. **Scheduler** (`app/scheduler.py`) — Returns the list of configured tracks from config (direct, validation, perspective)
3. **Track Execution** — All tracks run concurrently via `asyncio.gather`. Each track calls `adapter.generate(f"{track_name}:{request}")` and returns `{"track": <name>, "answer": <response>}`
4. **MergeEngine** (`app/merge.py`) — Merges track outputs with priority: direct > perspective > first available. Returns `{"answer": <chosen>, "sources": [<track_names>]}`
5. **Validator** (`app/validator.py`) — Validates the merged result: `{"pass": true, "confidence": 93, "drift": 2, "notes": ["mock validator"]}`
6. **MetricsRecorder** (`app/metrics.py`) — Stores validation + timing to SQLite via the storage layer

### Perspective Engine (`app/perspective_engine.py`)

Fully implemented `PerspectiveEngine` class with 12 specialized analysis viewpoints:

| Perspective | Focus Area |
|-------------|-----------|
| engineering | Technical feasibility, performance, scalability |
| scientific | Accuracy, methodology, evidence quality |
| business | ROI, market fit, commercial viability |
| economic | Cost-benefit, financial impact |
| security | Vulnerabilities, threat model, data protection |
| legal | Compliance, liability, intellectual property |
| ethics | Bias, fairness, social impact |
| ux | Usability, accessibility, user satisfaction |
| operations | Implementation, maintainability, support |
| education | Learning curve, documentation, knowledge transfer |
| risk | Failure modes, contingency, mitigation |
| design | Architecture, reliability, fault tolerance |

- Runs all perspective analyses in parallel via `asyncio.gather`
- Accepts an optional provider adapter; falls back to mock analysis
- Returns perspectives dict, count, and duration

### Provider-Independent Adapter System (`app/adapters/`)

| File | Class | Purpose |
|------|-------|---------|
| base.py | AdapterBase | Abstract base: generate(), stream(), health_check(), token_usage() |
| mock_adapter.py | MockAdapter | Deterministic mock provider (active) |
| openai_adapter.py | OpenAIAdapter | OpenAI stub (health_check=false) |
| anthropic_adapter.py | AnthropicAdapter | Anthropic stub (health_check=false) |
| gemini_adapter.py | GeminiAdapter | Gemini stub (health_check=false) |
| registry.py | AdapterRegistry | Maps provider names to adapter classes; falls back to MockAdapter on failure |

The registry pattern allows adding new providers without modifying the engine. Any unavailable or unknown provider automatically falls back to MockAdapter.

### Configuration (`app/config.py` + `config/*.yml`)

The `Config` class loads YAML files from `config/` with safe defaults:

| File | Keys | Default |
|------|------|---------|
| base.yml | provider | mock |
| tracks.yml | direct, validation, perspective | All with provider=mock |
| scheduler.yml | type | simple |

### SQLite Metrics Storage (`storage/database.py`)

- Thread-safe SQLite connection with `threading.Lock`
- Auto-creates `metrics` table: `(id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, payload TEXT NOT NULL)`
- Creates descending index on `ts` for efficient queries
- `insert(data)` — Serializes dict to JSON, inserts with timestamp
- `query(sql, params)` — Executes SELECT, returns rows
- Context manager support (`__enter__`/`__exit__`)

### Logger Utility (`util/logger.py`)

- Python `logging` module wrapper with consistent formatting
- Configurable via `LOG_LEVEL` environment variable
- Output: `[timestamp] [LEVEL] SPACE_BOUND_AI: message`

---

## Frontend: React/Vite TypeScript Dashboard

### Technology Stack
- React 18.3.1
- Vite 6.0.5
- TypeScript 5.7.2

### Dashboard Features (`web/src/App.tsx`)

| Panel | Function |
|-------|----------|
| Engine Run | Provider selector, prompt textarea, Run Engine button |
| Metrics | Confidence %, Drift %, Latency ms, Total Runs count |
| Run History | List of past runs with pass/fail, confidence, latency, timestamp |
| Configuration | Provider, scheduler, tracks, available providers |
| Status Header | Online/Offline indicator with pulsing dot |

### API Connections

The frontend connects to all 6 backend endpoints via Vite's dev server proxy (`web/vite.config.ts`):

| Frontend Action | Endpoint | Method |
|-----------------|----------|--------|
| Health check | /health | GET |
| Load config | /config | GET |
| Load metrics | /metrics | GET |
| Run engine | /chat | POST |
| Provider list | /providers | GET (via config) |
| Track list | /tracks | GET (via config) |

### Build Process

```bash
cd web && npm install && npm run build
```

Produces `web/dist/` with:
- `index.html` (0.40 KB)
- `assets/index-*.css` (5.03 KB)
- `assets/index-*.js` (149.12 KB)

The FastAPI server automatically serves these static files when `web/dist/` exists.

---

## Orchestration Flow

```
User Request (POST /chat)
    │
    ▼
BaselineBuilder.build(prompt)
    │ → {"request": prompt, "meta": {"now": timestamp}}
    ▼
Scheduler.schedule()
    │ → ["direct", "validation", "perspective"]
    ▼
asyncio.gather(*tracks)  ← concurrent execution
    │ → [{"track": "direct", "answer": "..."},
    │    {"track": "validation", "answer": "..."},
    │    {"track": "perspective", "answer": "..."}]
    ▼
MergeEngine.merge(results)
    │ → {"answer": "direct answer", "sources": ["direct"]}
    ▼
Validator.validate(merged)
    │ → {"pass": true, "confidence": 93, "drift": 2, "notes": [...]}
    ▼
MetricsRecorder.record({validation, timing})
    │ → SQLite INSERT
    ▼
Response: {answer, validation, timing}
```

## Validation Pipeline

The validator (`app/validator.py`) currently provides deterministic mock validation:

- **pass:** true
- **confidence:** 93
- **drift:** 2
- **notes:** ["mock validator"]

This is designed to be replaced with a real validation implementation that checks contradictions, context drift, hallucination risk, reasoning consistency, and policy alignment.
