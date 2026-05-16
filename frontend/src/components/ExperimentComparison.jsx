import React, { useState } from "react";

export default function ExperimentComparison({ runs }) {
  const [runAId, setRunAId] = useState("");
  const [runBId, setRunBId] = useState("");

  const runA = runs.find(r => r.id === runAId);
  const runB = runs.find(r => r.id === runBId);

  return (
    <div>
      <div style={{ display: "flex", gap: "20px", marginBottom: "30px" }}>
        <div style={{ flex: 1 }}>
          <label style={{ display: "block", marginBottom: "8px", fontSize: "0.9rem" }}>Baseline Run (A)</label>
          <select 
            className="input" 
            value={runAId} 
            onChange={(e) => setRunAId(e.target.value)}
          >
            <option value="">Select a run...</option>
            {runs.map(r => <option key={r.id} value={r.id}>{r.id} ({r.dataset_id})</option>)}
          </select>
        </div>
        <div style={{ flex: 1 }}>
          <label style={{ display: "block", marginBottom: "8px", fontSize: "0.9rem" }}>Comparison Run (B)</label>
          <select 
            className="input" 
            value={runBId} 
            onChange={(e) => setRunBId(e.target.value)}
          >
            <option value="">Select a run...</option>
            {runs.map(r => <option key={r.id} value={r.id}>{r.id} ({r.dataset_id})</option>)}
          </select>
        </div>
      </div>

      {runA && runB ? (
        <div className="card" style={{ padding: "0" }}>
          <h3 style={{ padding: "20px", margin: 0, borderBottom: "1px solid var(--color-border)" }}>Metric Comparison</h3>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", borderBottom: "2px solid var(--color-border)" }}>
                <th style={{ padding: "15px" }}>Metric</th>
                <th style={{ padding: "15px" }}>Run A</th>
                <th style={{ padding: "15px" }}>Run B</th>
                <th style={{ padding: "15px" }}>Delta</th>
              </tr>
            </thead>
            <tbody>
              <ComparisonRow label="Groundedness" valA={runA.metrics_summary?.avg_groundedness} valB={runB.metrics_summary?.avg_groundedness} />
              <ComparisonRow label="Relevance" valA={runA.metrics_summary?.avg_relevance} valB={runB.metrics_summary?.avg_relevance} />
              <ComparisonRow label="Hit Rate" valA={runA.metrics_summary?.hit_rate} valB={runB.metrics_summary?.hit_rate} isPercent />
              <ComparisonRow label="Recall" valA={runA.metrics_summary?.avg_recall} valB={runB.metrics_summary?.avg_recall} isPercent />
              <ComparisonRow label="Latency (ms)" valA={runA.metrics_summary?.avg_latency_ms} valB={runB.metrics_summary?.avg_latency_ms} isInverted />
            </tbody>
          </table>
        </div>
      ) : (
        <div style={{ textAlign: "center", padding: "40px", color: "rgba(255,255,255,0.4)" }}>
          Select two runs above to compare their performance.
        </div>
      )}
    </div>
  );
}

function ComparisonRow({ label, valA, valB, isPercent = false, isInverted = false }) {
  if (valA === undefined || valB === undefined) return null;

  const delta = valB - valA;
  const deltaPct = valA !== 0 ? (delta / valA) * 100 : 0;
  
  // For most metrics, higher is better. For latency, lower is better.
  const isBetter = isInverted ? delta < 0 : delta > 0;
  const isWorse = isInverted ? delta > 0 : delta < 0;
  
  const color = isBetter ? "#4CAF50" : (isWorse ? "#ff4d4d" : "inherit");
  const sign = delta > 0 ? "+" : "";

  const format = (v) => isPercent ? `${(v * 100).toFixed(1)}%` : v.toFixed(2);

  return (
    <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
      <td style={{ padding: "15px" }}>{label}</td>
      <td style={{ padding: "15px" }} className="mono">{format(valA)}</td>
      <td style={{ padding: "15px" }} className="mono">{format(valB)}</td>
      <td style={{ padding: "15px", color, fontWeight: "bold" }} className="mono">
        {sign}{format(delta)} ({sign}{deltaPct.toFixed(1)}%)
      </td>
    </tr>
  );
}
