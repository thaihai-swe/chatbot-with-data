import React from "react";

export default function RunDetail({ run, onBack }) {
  if (!run) return null;

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: "15px", marginBottom: "20px" }}>
        <button className="button button-outline" onClick={onBack} style={{ padding: "4px 12px" }}>← Back</button>
        <h2 style={{ margin: 0 }}>Run Detail: <span className="mono">{run.id}</span></h2>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px", marginBottom: "30px" }}>
        <MetricCard label="Groundedness" value={run.metrics_summary?.avg_groundedness} />
        <MetricCard label="Relevance" value={run.metrics_summary?.avg_relevance} />
        <MetricCard label="Hit Rate" value={run.metrics_summary?.hit_rate} isPercent />
        <MetricCard label="Latency" value={run.metrics_summary?.avg_latency_ms} unit="ms" />
      </div>

      <div className="card" style={{ padding: "0" }}>
        <h3 style={{ padding: "20px", margin: 0, borderBottom: "1px solid var(--color-border)" }}>Test Case Results</h3>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "2px solid var(--color-border)" }}>
                <th style={{ padding: "12px" }}>Case ID</th>
                <th style={{ padding: "12px" }}>Groundedness</th>
                <th style={{ padding: "12px" }}>Relevance</th>
                <th style={{ padding: "12px" }}>Hit</th>
                <th style={{ padding: "12px" }}>Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {run.results.map(result => (
                <tr key={result.case_id} style={{ borderBottom: "1px solid var(--color-border)", verticalAlign: "top" }}>
                  <td style={{ padding: "12px" }} className="mono">{result.case_id}</td>
                  <td style={{ padding: "12px" }}>
                    <ScoreBadge score={result.metrics?.groundedness?.score} />
                  </td>
                  <td style={{ padding: "12px" }}>
                    <ScoreBadge score={result.metrics?.relevance?.score} />
                  </td>
                  <td style={{ padding: "12px" }}>
                    {result.metrics?.hit ? "✅" : "❌"}
                  </td>
                  <td style={{ padding: "12px", fontSize: "0.85rem" }}>
                    <div style={{ marginBottom: "5px" }}><strong>G:</strong> {result.metrics?.groundedness?.reason || "-"}</div>
                    <div><strong>R:</strong> {result.metrics?.relevance?.reason || "-"}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, unit = "", isPercent = false }) {
  const displayValue = value !== undefined 
    ? (isPercent ? `${(value * 100).toFixed(0)}%` : value.toFixed(2))
    : "-";

  return (
    <div className="card" style={{ textAlign: "center", background: "rgba(255,255,255,0.05)" }}>
      <div style={{ fontSize: "0.8rem", color: "rgba(255,255,255,0.6)", marginBottom: "5px" }}>{label}</div>
      <div style={{ fontSize: "1.5rem", fontWeight: "bold", color: "var(--color-primary)" }}>
        {displayValue}{unit && <span style={{ fontSize: "0.9rem", marginLeft: "2px" }}>{unit}</span>}
      </div>
    </div>
  );
}

function ScoreBadge({ score }) {
  if (score === undefined) return <span>-</span>;
  
  let color = "#ff4d4d"; // Red
  if (score >= 0.8) color = "#4CAF50"; // Green
  else if (score >= 0.5) color = "#FFC107"; // Yellow

  return (
    <span style={{ 
      display: "inline-block", padding: "2px 8px", borderRadius: "4px", 
      background: color + "20", color: color, fontWeight: "bold", fontSize: "0.8rem",
      border: `1px solid ${color}40`
    }}>
      {score.toFixed(1)}
    </span>
  );
}
