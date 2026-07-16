SPACE_BOUND_AI 🚀

SPACE_BOUND_AI is an AI orchestration framework and demonstration platform that coordinates multiple reasoning tracks through a unified execution pipeline.

The system runs independent processing paths for:

- Direct response generation
- Validation and consistency checking
- Perspective expansion and analysis

Results are synthesized into a final response while tracking execution metrics, latency, provider usage, and validation data.

SPACE_BOUND_AI includes:

- FastAPI backend
- Pluggable AI model adapters
- Async orchestration engine
- SQLite metric storage
- React/Vite dashboard
- Automated test suite

---

Core Architecture

Request
   |
   v
Baseline Context
   |
   v
Scheduler
   |
   +----------------+
   |                |
   v                v
Direct Track    Perspective Track
   |
   v
Validation Track
   |
   v
Synthesis Engine
   |
   v
Metrics Storage
   |
   v
Final Response

The architecture is designed around parallel processing, modular providers, and measurable execution.

---

Features

Async Orchestration Engine

The core engine manages:

- Request lifecycle
- Request IDs
- Execution timing
- Track coordination
- Error handling
- Provider selection
- Response synthesis

---

Multi-Track Reasoning Pipeline

SPACE_BOUND_AI currently supports:

Track 1: Direct Response

Generates the primary response from the selected model adapter.

Track 2: Validation

Checks:

- Context consistency
- Contradictions
- Drift indicators
- Confidence scoring
- Response quality signals

Track 3: Perspective Analysis

Provides additional viewpoints using relevant analysis categories.

Available perspective categories include:

- Engineering
- Scientific
- Business
- Economic
- Security
- Legal
- Ethics
- UX
- Operations
- Education
- Risk Analysis
- System Design

---

Technology Stack

Backend

- Python 3.10+
- FastAPI
- Pydantic
- AsyncIO
- SQLite
- PyYAML
- Uvicorn

Frontend

- TypeScript
- React
- Vite

Testing

- Pytest
- FastAPI TestClient
- Async test coverage

---

Repository Structure

SPACE_BOUND_AI/

├── app/
│   ├── engine.py
│   ├── scheduler.py
│   ├── validator.py
│   ├── perspective_engine.py
│   ├── merge.py
│   ├── metrics.py
│   └── adapters/
│
├── config/
│   ├── base.yml
│   ├── tracks.yml
│   ├── scheduler.yml
│   └── providers.yml
│
├── storage/
│   └── database.py
│
├── web/
│   └── React dashboard
│
├── tests/
│   ├── test_api.py
│   ├── test_core_additional.py
│   └── test_engine.py
│
├── main.py
├── requirements.txt
└── LICENSE

---

Installation

Requirements

- Python 3.10+
- Node.js 18+
- npm

---

Backend Setup

Create a virtual environment:

python -m venv .venv

Activate:

Linux/macOS:

source .venv/bin/activate

Windows:

.\.venv\Scripts\activate

Install dependencies:

pip install --upgrade pip
pip install -r requirements.txt

---

Frontend Build

From the repository root:

cd web
npm ci
npm run build
cd ..

The production dashboard build is generated in:

web/dist

---

Running the Application

Start the backend:

uvicorn main:app --reload --host 0.0.0.0 --port 8000

The API will be available at:

http://localhost:8000

---

API Endpoints

Health Check

GET /health

Returns service status.

---

Providers

GET /providers

Returns available model adapters.

---

Tracks

GET /tracks

Returns configured reasoning tracks.

---

Configuration

GET /config

Returns active configuration.

---

Metrics

GET /metrics

Returns stored execution metrics.

---

Chat

POST /chat

Example:

{
  "prompt": "Explain quantum computing simply."
}

The default provider is:

mock

The mock provider requires no API keys.

---

Model Adapter System

SPACE_BOUND_AI uses a modular adapter architecture.

Supported adapters:

- Mock
- OpenAI
- Anthropic
- Gemini
- Ollama
- LM Studio
- Local Llama-compatible providers

The adapter interface supports:

- generate()
- stream()
- health_check()
- token_usage()

External providers require environment variables.

Examples:

OPENAI_API_KEY
ANTHROPIC_API_KEY
GEMINI_API_KEY

No credentials are required for the default mock provider.

---

Metrics and Storage

SPACE_BOUND_AI stores execution information using SQLite.

Tracked data includes:

- Request ID
- Timestamp
- Provider
- Latency
- Token usage
- Cost estimate
- Validation results
- Perspective results
- Execution metrics

---

Testing

The repository includes automated tests covering:

- API endpoints
- Engine execution
- Scheduler behavior
- Validation pipeline
- Merge logic
- Adapter framework
- Configuration
- Metrics handling
- Error handling
- Concurrency behavior

Verified Test Status

Current repository verification:

47 passed
0 failed

Test breakdown:

Test File| Count
tests/test_api.py| 8
tests/test_core_additional.py| 24
tests/test_engine.py| 15
Total| 47

Run tests:

PYTHONPATH=. pytest tests/ -v

---

Development Verification

Compile Python files:

python -m compileall .

Run the test suite:

PYTHONPATH=. pytest tests/ -v

---

Dashboard

The React dashboard provides visibility into:

- Current prompts
- Track outputs
- Validation results
- Perspective analysis
- Final synthesis
- Latency
- Provider information
- Execution metrics

Build the frontend:

cd web
npm ci
npm run build

---

Configuration

Configuration files:

config/base.yml
config/tracks.yml
config/scheduler.yml
config/providers.yml
config/dashboard.yml

The default configuration uses:

provider: mock

This allows the project to run without external API access.

---

Roadmap

Potential future improvements:

- Authentication layer
- Production deployment tooling
- Advanced model-based validation
- Expanded benchmark suite
- More provider integrations
- Distributed execution support
- Enterprise observability features

---

License

SPACE_BOUND_AI is licensed under the Apache License 2.0.

See:

LICENSE

for details.
