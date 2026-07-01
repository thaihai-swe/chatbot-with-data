import React, { useState } from "react";
import { runSanityCheck } from "../api/chat";

export default function EvaluationScreen() {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleRunEval = async () => {
    setIsRunning(true);
    setResults(null);
    setError(null);
    try {
      const data = await runSanityCheck();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="page-shell">
      <div className="hero">
        <div>
          <span className="eyebrow">Quality Assurance</span>
          <h1>System Evaluation</h1>
          <p className="hero-copy">Run side-by-side verification against the Golden Dataset to measure retrieval recall and response groundedness.</p>
        </div>
      </div>

      <div className="panel glassmorphic">
        <div className="panel-heading">
          <div>
            <h3>Golden Dataset Sanity Check</h3>
            <p>Executes 20+ core scenarios and scores them using LLM-as-a-judge.</p>
          </div>
          <button 
            onClick={handleRunEval} 
            className="button button-primary" 
            disabled={isRunning}
            style={{ height: "48px", padding: "0 32px" }}
          >
            {isRunning ? "Evaluating System..." : "Start Sanity Check"}
          </button>
        </div>

        {error && (
          <div className="error-banner">
            <strong>Evaluation Failed:</strong> {error}
          </div>
        )}

        {isRunning && (
          <div className="empty-state">
            <div className="spinner" style={{ marginBottom: "24px" }}></div>
            <p className="mono" style={{ fontSize: "14px", fontWeight: "600" }}>Analyzing system performance across test cases...</p>
            <p style={{ fontSize: "13px", opacity: 0.7, marginTop: "8px" }}>This process typically takes 45-60 seconds.</p>
          </div>
        )}

        {results && (
          <div style={{ marginTop: "32px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 2.2fr", gap: "32px", alignItems: "start" }}>
              
              {/* Left Column: Summary Metrics Stack */}
              <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
                
                {/* Accuracy Score Card */}
                <div className="surface-card glassmorphic" style={{ padding: "24px", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)" }}>
                  <span className="eyebrow" style={{ fontSize: "11px", color: "var(--accent)" }}>System Pass Rate</span>
                  <div style={{ display: "flex", alignItems: "baseline", gap: "8px", marginTop: "12px" }}>
                    <span style={{ fontSize: "40px", fontWeight: "800", color: "var(--text-primary)", fontFamily: "var(--font-display)", letterSpacing: "-0.04em" }}>
                      {((results.passed_cases / results.total_cases) * 100).toFixed(0)}%
                    </span>
                    <span style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: "600" }}>
                      ({results.passed_cases}/{results.total_cases}) Passed
                    </span>
                  </div>
                  <div style={{ width: "100%", height: "6px", background: "var(--border)", borderRadius: "var(--radius-full)", marginTop: "16px", overflow: "hidden" }}>
                    <div style={{ width: `${(results.passed_cases / results.total_cases) * 100}%`, height: "100%", background: "var(--success)" }}></div>
                  </div>
                </div>

                {/* Avg Recall Card */}
                <div className="surface-card glassmorphic" style={{ padding: "24px", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)" }}>
                  <span className="eyebrow" style={{ fontSize: "11px", color: "var(--accent)" }}>Avg Retrieval Recall</span>
                  <div style={{ display: "flex", alignItems: "baseline", gap: "8px", marginTop: "12px" }}>
                    <span style={{ fontSize: "40px", fontWeight: "800", color: "var(--text-primary)", fontFamily: "var(--font-display)", letterSpacing: "-0.04em" }}>
                      {(results.overall_recall * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div style={{ width: "100%", height: "6px", background: "var(--border)", borderRadius: "var(--radius-full)", marginTop: "16px", overflow: "hidden" }}>
                    <div style={{ width: `${results.overall_recall * 100}%`, height: "100%", background: "var(--accent)" }}></div>
                  </div>
                </div>

                {/* Groundedness Card */}
                <div className="surface-card glassmorphic" style={{ padding: "24px", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)" }}>
                  <span className="eyebrow" style={{ fontSize: "11px", color: "var(--warning)" }}>Response Groundedness</span>
                  <div style={{ display: "flex", alignItems: "baseline", gap: "8px", marginTop: "12px" }}>
                    <span style={{ fontSize: "40px", fontWeight: "800", color: "var(--text-primary)", fontFamily: "var(--font-display)", letterSpacing: "-0.04em" }}>
                      {(results.overall_groundedness * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div style={{ width: "100%", height: "6px", background: "var(--border)", borderRadius: "var(--radius-full)", marginTop: "16px", overflow: "hidden" }}>
                    <div style={{ width: `${results.overall_groundedness * 100}%`, height: "100%", background: "var(--warning)" }}></div>
                  </div>
                </div>
              </div>

              {/* Right Column: Detailed LLM-as-a-judge verdicts table */}
              <div className="table-scroll glassmorphic" style={{ borderRadius: "var(--radius-xl)", border: "1px solid var(--glass-border)", overflow: "hidden" }}>
                <table>
                  <thead>
                    <tr>
                      <th>Scenario</th>
                      <th>Question</th>
                      <th style={{ textAlign: "center" }}>Recall</th>
                      <th style={{ textAlign: "center" }}>Grounded</th>
                      <th style={{ textAlign: "center" }}>Latency</th>
                      <th style={{ textAlign: "right" }}>Verdict</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.results.map((r) => (
                      <tr key={r.case_id}>
                        <td className="mono" style={{ fontSize: "12px", fontWeight: "700" }}>{r.case_id}</td>
                        <td style={{ maxWidth: "400px" }}>
                          <div style={{ fontWeight: "600", fontSize: "14px" }}>{r.question}</div>
                          {r.groundedness_reason && (
                            <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "6px", fontStyle: "italic", borderLeft: "2px solid var(--border)", paddingLeft: "10px" }}>
                              {r.groundedness_reason}
                            </div>
                          )}
                        </td>
                        <td style={{ textAlign: "center" }}>
                          <span className={`status-badge ${r.recall_status ? "status-success" : "status-danger"}`} style={{ height: "20px", fontSize: "10px" }}>
                            {r.recall_status ? "MATCH" : "MISS"}
                          </span>
                        </td>
                        <td style={{ textAlign: "center", fontWeight: "700" }}>
                          <span style={{ color: r.groundedness_score > 0.8 ? "var(--success)" : "var(--text-primary)" }}>
                            {(r.groundedness_score * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td style={{ textAlign: "center" }} className="mono">{r.latency_ms}ms</td>
                        <td style={{ textAlign: "right" }}>
                          <span className={`status-badge ${r.passed ? "status-success" : "status-danger"}`} style={{ minWidth: "80px", justifyContent: "center" }}>
                            {r.passed ? "PASS" : "FAIL"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
