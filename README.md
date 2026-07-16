# SPACE_BOUND_AI

SPACE_BOUND_AI is a small orchestration service and demo that runs multiple "tracks" (direct, validation, perspective) against pluggable model adapters and records metrics to a local SQLite storage. It provides a FastAPI backend and a small React dashboard (in web/) to view results.

This README has been updated to accurately reflect repository structure, how to run the project locally, and what environment variables may be required.

## Stack
- Language: Python 3.10+ (backend), TypeScript / React (frontend)
- Frameworks: FastAPI (backend), Vite + React (frontend)
- Notable libraries: pydantic, uvicorn, aiohttp, PyYAML

## Repository layout

Top-level files and directories you will care about:

- app/           Application code: Engine, Validator, Adapters, Metrics, Scheduler, etc.
  - adapters/    Provider adapters (mock, openai, anthropic, gemini)
- config/        YAML configuration for base, tracks, scheduler, dashboard
- storage/       SQLite wrapper and DB initialization
- util/          Utility modules (logger, helpers)
- web/           React dashboard (package.json, src/, vite.config.ts)
- tests/         Pytest test suite
- main.py        FastAPI application entrypoint
- requirements.txt  Python dependencies
- LICENSE        Apache 2.0 license

## How to run (local development)

Prerequisites:
- Python 3.10 or newer
- Node 18+ and npm
- (Optional) virtualenv/venv recommended

1) Create and activate a Python virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.\.venv\Scripts\activate  # Windows (PowerShell)
```

2) Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3) Build the frontend (from repo root)

```bash
cd web
npm ci
npm run build
cd ..
```

This produces a static build under `web/dist` that the FastAPI app will serve (if present).

4) Optional: compile Python files to check syntax

```bash
python -m compileall .
```

5) Run tests

```bash
PYTHONPATH=. pytest tests/ -v
```

6) Start the backend

```bash
# development: run uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The app exposes these key endpoints (JSON):
- GET /health      — service heartbeat
- GET /providers   — active/available providers
- GET /tracks      — configured orchestration tracks
- GET /config      — configuration summary
- GET /metrics     — recent metric records (from SQLite)
- POST /chat       — run orchestration for a prompt

Example POST /chat payload:

```json
{
  "prompt": "Test SPACE_BOUND_AI full orchestration pipeline"
}
```

If you omit `provider`, the default configured provider in `config/base.yml` is used (defaults to `mock`). The `mock` adapter requires no credentials and is used by the test-suite.

## Configuration and environment variables

- Config files live in `config/`:
  - `base.yml` — base settings (provider, etc.)
  - `tracks.yml` — track definitions (direct, validation, perspective)
  - `scheduler.yml` — scheduler configuration
  - `providers.yml` / `dashboard.yml` — dashboard/provider-specific settings

- Adapters that call external LLM APIs (openai, anthropic, gemini) will likely require API keys in the environment. The project expects you to set provider-specific environment variables if you switch from the `mock` adapter. Common examples (NOT exhaustive):
  - OPENAI_API_KEY
  - ANTHROPIC_API_KEY
  - GEMINI_API_KEY

Tests and the default configuration use the mock adapter — you do not need API keys to run the test-suite.

## Metrics / Storage

Metrics are stored via the small SQLite wrapper in `storage/database.py`. By default it will create local files in the working directory as needed. Ensure the directory where you run the server has write permissions.

## Frontend

The frontend is a small React + Vite app in `web/`. `npm ci` installs dependencies deterministically from `package-lock.json`. `npm run build` outputs a production build to `web/dist` which the backend serves when present.

## Tests

The test-suite uses pytest and the FastAPI TestClient. Tests exercise the Engine, adapters (mock), Validator, MergeEngine, Scheduler, and the API endpoints via TestClient. Run with:

```bash
PYTHONPATH=. pytest tests/ -v
```

## License

This project is licensed under the Apache License 2.0 — see `LICENSE` at the repository root.

## Troubleshooting and common issues

- If pytest fails with import errors, ensure you ran `pip install -r requirements.txt` and are running tests from the repository root with `PYTHONPATH=.` set.
- If the frontend fails to build, confirm your Node.js and npm versions and run `npm ci` from the `web/` directory.
- If adapters attempt to call external APIs and fail, switch to the `mock` provider in `config/base.yml` to run locally without credentials.

## Want me to update anything else?
If you would like, I can:
- Add a GitHub Actions workflow to run the verification pipeline automatically.
- Open a PR that updates the README only (if you grant write permissions or create a branch and allow me to push).

