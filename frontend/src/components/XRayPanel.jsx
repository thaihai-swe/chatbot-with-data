import React from "react";

export default function XRayPanel({ trace, onClose }) {
  if (!trace) return null;

  const { retrieval, safety, evaluation } = trace;

  return (
    <div className="xray-panel">
      <div className="xray-header">
        <h3>Pipeline X-Ray</h3>
        <button onClick={onClose} className="button button-outline" style={{ padding: "4px 8px" }}>Close</button>
      </div>
      
      <div className="xray-content">
        {/* Groundedness & Safety Section */}
        <section className="xray-section">
          <h4 className="xray-section-title">Safety & Grounding</h4>
          <div className="xray-grid">
            <div className="xray-metric">
              <span className="xray-label">Groundedness</span>
              <span className={`xray-value ${safety?.groundedness?.score >= 0.7 ? "text-success" : "text-danger"}`}>
                {safety?.groundedness?.score !== undefined ? (safety.groundedness.score * 100).toFixed(0) + "%" : "N/A"}
              </span>
            </div>
            <div className="xray-metric">
              <span className="xray-label">Risk</span>
              <span className={`xray-value ${safety?.injection_risk === "low" ? "text-success" : "text-danger"}`}>
                {safety?.injection_risk?.toUpperCase() || "UNKNOWN"}
              </span>
            </div>
            <div className="xray-metric">
              <span className="xray-label">Intent</span>
              <span className="xray-value">{retrieval?.classification || "Baseline"}</span>
            </div>
          </div>
          {safety?.classifier_reason && (
            <div className="xray-reason">{safety.classifier_reason}</div>
          )}
        </section>

        {/* Retrieval Transformations */}
        {retrieval?.transformations && (
          <section className="xray-section">
            <h4 className="xray-section-title">Query Transformations</h4>
            {retrieval.transformations.rewritten_query && (
              <div className="xray-item">
                <span className="xray-label-small">Rewritten</span>
                <div className="xray-text">{retrieval.transformations.rewritten_query}</div>
              </div>
            )}
            {retrieval.transformations.expanded_queries?.length > 0 && (
              <div className="xray-item">
                <span className="xray-label-small">Expansion ({retrieval.transformations.expanded_queries.length})</span>
                <ul className="xray-list">
                  {retrieval.transformations.expanded_queries.map((q, i) => <li key={i}>{q}</li>)}
                </ul>
              </div>
            )}
            {retrieval.transformations.hyde_doc && (
              <div className="xray-item">
                <span className="xray-label-small">HyDE Generation</span>
                <div className="xray-text-scroll">{retrieval.transformations.hyde_doc}</div>
              </div>
            )}
          </section>
        )}

        {/* Strategy & Routing */}
        <section className="xray-section">
          <h4 className="xray-section-title">Routing & Strategy</h4>
          <div className="xray-item">
            <span className="xray-label-small">Selected Strategy</span>
            <div className="mono" style={{ fontSize: "0.8rem", color: "var(--color-primary)" }}>
              {retrieval?.routing?.selected_strategy?.toUpperCase()}
            </div>
          </div>
          {retrieval?.routing?.reason && (
            <div className="xray-reason">{retrieval.routing.reason}</div>
          )}
        </section>

        {/* Retrieval Runs */}
        {retrieval?.retrieval_runs?.length > 0 && (
          <section className="xray-section">
            <h4 className="xray-section-title">Retrieval Runs ({retrieval.retrieval_runs.length})</h4>
            <div className="xray-list-container">
              {retrieval.retrieval_runs.map((run, i) => (
                <div key={i} className="xray-run-item">
                  <div className="mono" style={{ fontSize: "0.7rem", opacity: 0.7, overflow: "hidden", textOverflow: "ellipsis" }}>{run.query}</div>
                  <div style={{ fontSize: "0.7rem", marginTop: "2px" }}>
                    Found {run.raw_count} chunks. Max score: {run.top_scores?.length > 0 ? Math.max(...run.top_scores).toFixed(3) : "0"}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Latency */}
        <section className="xray-section">
          <h4 className="xray-section-title">Performance</h4>
          <div className="xray-grid">
            {Object.entries(retrieval?.execution_time_ms || {}).map(([key, val]) => (
              <div key={key} className="xray-metric-small">
                <span className="xray-label-small">{key}</span>
                <span className="mono">{val}ms</span>
              </div>
            ))}
          </div>
        </section>

        {/* Raw JSON Toggle */}
        <details style={{ marginTop: "20px" }}>
          <summary style={{ cursor: "pointer", fontSize: "0.7rem", opacity: 0.5 }}>View Raw Trace JSON</summary>
          <pre className="mono" style={{ fontSize: "0.65rem", marginTop: "10px", padding: "10px", background: "#f5f5f5", borderRadius: "4px", overflowX: "auto" }}>
            {JSON.stringify(trace, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}
