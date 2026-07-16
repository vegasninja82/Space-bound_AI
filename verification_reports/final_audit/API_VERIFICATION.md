# SPACE_BOUND_AI — API Verification

All endpoints are defined in `main.py` and were verified against a live server instance.

---

## GET /health

**Purpose:** Health check endpoint.

**Request:**
```
GET /health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "version": "1.0"
}
```

**Verified:** PASS — Returns 200 with status "ok" and version "1.0".

---

## GET /providers

**Purpose:** List active and available provider adapters.

**Request:**
```
GET /providers
```

**Response (200 OK):**
```json
{
  "active": "mock",
  "available": ["mock", "openai", "anthropic", "gemini"]
}
```

**Verified:** PASS — Returns active provider "mock" and 4 available providers.

---

## GET /tracks

**Purpose:** List configured reasoning tracks.

**Request:**
```
GET /tracks
```

**Response (200 OK):**
```json
{
  "tracks": ["direct", "validation", "perspective"]
}
```

**Verified:** PASS — Returns 3 tracks: direct, validation, perspective.

---

## GET /config

**Purpose:** Return full engine configuration.

**Request:**
```
GET /config
```

**Response (200 OK):**
```json
{
  "provider": "mock",
  "tracks": ["direct", "validation", "perspective"],
  "scheduler": {
    "type": "simple",
    "afterthought_window": 3,
    "parallel_tracks": true
  },
  "providers": ["mock", "openai", "anthropic", "gemini"]
}
```

**Verified:** PASS — Returns provider, tracks, scheduler config, and available providers.

---

## GET /metrics

**Purpose:** Retrieve recent run metrics from SQLite storage (last 50 records).

**Request:**
```
GET /metrics
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "ts": 1784233003.1389854,
    "data": {
      "validation": {
        "pass": true,
        "confidence": 93,
        "drift": 2,
        "notes": ["mock validator"]
      },
      "timing": {
        "total_ms": 0
      }
    }
  }
]
```

**Verified:** PASS — Returns array of metric records ordered by id DESC, limit 50.

---

## POST /chat

**Purpose:** Execute the multi-track reasoning pipeline.

**Request:**
```
POST /chat
Content-Type: application/json

{
  "prompt": "Analyze secure database migration architecture",
  "provider": "mock"
}
```

**Field Reference:**
| Field | Type | Required | Default |
|-------|------|----------|---------|
| prompt | string | Yes | — |
| provider | string \| null | No | "mock" (from config) |

**Response (200 OK):**
```json
{
  "answer": "MOCK_ANSWER: deterministic answer for: direct:Analyze secure database migration architecture",
  "validation": {
    "pass": true,
    "confidence": 93,
    "drift": 2,
    "notes": ["mock validator"]
  },
  "timing": {
    "total_ms": 0
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "detail": "Prompt is required"
}
```

**Verified:** PASS — Returns answer from merged tracks, validation results, and timing. Empty prompt correctly returns 400.

---

## Pipeline Flow (triggered by POST /chat)

1. **BaselineBuilder** creates request context with timestamp
2. **Scheduler** returns all configured tracks (direct, validation, perspective)
3. **Engine.run_track** executes each track concurrently via `asyncio.gather`
4. **MergeEngine** merges track outputs (priority: direct > perspective > first available)
5. **Validator** validates the merged result (confidence, drift, notes)
6. **MetricsRecorder** stores validation + timing to SQLite
7. Response returned with answer, validation, and timing
