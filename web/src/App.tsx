import { useState, useEffect, useCallback } from "react";

interface RunResult {
  answer: string;
  validation: {
    pass: boolean;
    confidence: number;
    drift: number;
    notes: string[];
  };
  timing: { total_ms: number };
}

interface MetricEntry {
  id: number;
  ts: number;
  data: {
    validation?: { pass?: boolean; confidence?: number; drift?: number };
    timing?: { total_ms?: number };
  };
}

interface ConfigInfo {
  provider: string;
  tracks: string[];
  scheduler: string;
  providers: string[];
}

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [provider, setProvider] = useState("mock");
  const [result, setResult] = useState<RunResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [metrics, setMetrics] = useState<MetricEntry[]>([]);
  const [config, setConfig] = useState<ConfigInfo | null>(null);
  const [health, setHealth] = useState(false);

  const fetchConfig = useCallback(async () => {
    try {
      const res = await fetch("/api/config");
      if (res.ok) setConfig(await res.json());
    } catch {}
  }, []);

  const fetchHealth = useCallback(async () => {
    try {
      const res = await fetch("/api/health");
      setHealth(res.ok);
    } catch {
      setHealth(false);
    }
  }, []);

  const fetchMetrics = useCallback(async () => {
    try {
      const res = await fetch("/api/metrics");
      if (res.ok) setMetrics(await res.json());
    } catch {}
  }, []);

  useEffect(() => {
    fetchConfig();
    fetchHealth();
    fetchMetrics();
  }, [fetchConfig, fetchHealth, fetchMetrics]);

  const runEngine = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, provider }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Request failed");
      }
      const data: RunResult = await res.json();
      setResult(data);
      fetchMetrics();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const lastConfidence = result?.validation.confidence ?? metrics[0]?.data.validation?.confidence ?? 0;
  const lastDrift = result?.validation.drift ?? metrics[0]?.data.validation?.drift ?? 0;
  const lastLatency = result?.timing.total_ms ?? metrics[0]?.data.timing?.total_ms ?? 0;
  const totalRuns = metrics.length;

  return (
    <div className="app">
      <header className="header">
        <h1>SPACE_BOUND_AI</h1>
        <div className="status">
          <span className="status-dot" style={{ background: health ? "var(--success)" : "var(--error)" }} />
          {health ? "Engine Online" : "Engine Offline"}
        </div>
      </header>

      <main className="main">
        <div className="grid">
          <div className="card">
            <h2>Engine Run</h2>
            <div className="input-group">
              <select
                className="provider-select"
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
              >
                {(config?.providers ?? ["mock"]).map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div className="input-group">
              <textarea
                placeholder="Enter your prompt..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && e.ctrlKey) runEngine();
                }}
              />
            </div>
            <button className="btn" onClick={runEngine} disabled={loading || !prompt.trim()}>
              {loading ? "Running..." : "Run Engine"}
            </button>

            {error && <div className="error" style={{ marginTop: "1rem" }}>{error}</div>}

            {result && (
              <div style={{ marginTop: "1rem" }}>
                <div className="tracks">
                  {config?.tracks.map((t) => (
                    <span key={t} className="track-badge">{t}</span>
                  ))}
                </div>
                <div className="result-box">{result.answer}</div>
              </div>
            )}
          </div>

          <div className="card">
            <h2>Metrics</h2>
            <div className="metrics-grid">
              <div className="metric">
                <div className="value success">{lastConfidence}%</div>
                <div className="label">Confidence</div>
              </div>
              <div className="metric">
                <div className="value warning">{lastDrift}%</div>
                <div className="label">Drift</div>
              </div>
              <div className="metric">
                <div className="value accent">{lastLatency}ms</div>
                <div className="label">Latency</div>
              </div>
              <div className="metric">
                <div className="value primary">{totalRuns}</div>
                <div className="label">Total Runs</div>
              </div>
            </div>

            {result?.validation.notes && result.validation.notes.length > 0 && (
              <div style={{ marginTop: "1rem" }}>
                <h2>Validation Notes</h2>
                <ul style={{ listStyle: "none", fontSize: "0.8125rem", color: "var(--text-muted)" }}>
                  {result.validation.notes.map((note, i) => (
                    <li key={i} style={{ padding: "0.25rem 0" }}>• {note}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        <div className="grid">
          <div className="card">
            <h2>Run History</h2>
            {metrics.length === 0 ? (
              <div className="loading">No runs yet. Execute a prompt to see metrics.</div>
            ) : (
              <div className="history-list">
                {metrics.map((m) => {
                  const conf = m.data.validation?.confidence ?? 0;
                  const passed = m.data.validation?.pass ?? false;
                  const ms = m.data.timing?.total_ms ?? 0;
                  return (
                    <div key={m.id} className="history-item">
                      <span className={`conf ${passed ? "pass" : "fail"}`}>
                        {passed ? "PASS" : "FAIL"} {conf}%
                      </span>
                      <span>{ms}ms</span>
                      <span className="time">
                        {new Date(m.ts * 1000).toLocaleTimeString()}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="card">
            <h2>Configuration</h2>
            {config ? (
              <>
                <div className="config-row">
                  <span className="key">Provider</span>
                  <span className="val">{config.provider}</span>
                </div>
                <div className="config-row">
                  <span className="key">Scheduler</span>
                  <span className="val">{config.scheduler?.type ?? config.scheduler}</span>
                </div>
                <div className="config-row">
                  <span className="key">Tracks</span>
                  <span className="val">{config.tracks.join(", ")}</span>
                </div>
                <div className="config-row">
                  <span className="key">Available Providers</span>
                  <span className="val">{config.providers.join(", ")}</span>
                </div>
              </>
            ) : (
              <div className="loading">Loading config...</div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
