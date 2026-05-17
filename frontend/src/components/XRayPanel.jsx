import React from "react";

export default function XRayPanel({ trace, onClose }) {
  if (!trace) return null;

  const { retrieval, safety, evaluation } = trace;

  return (
    <div className="xray-panel" style={{ background: "var(--surface)", borderLeft: "1px solid var(--border)", boxShadow: "var(--shadow-lg)" }}>
      <div className="xray-header" style={{ padding: "16px 24px", borderBottom: "1px solid var(--border)", background: "var(--surface-muted)" }}>
        <h3 style={{ margin: 0, fontSize: "16px", fontWeight: "600" }}>Pipeline X-Ray</h3>
        <button onClick={onClose} className="button button-ghost" style={{ padding: "0 8px", height: "28px", fontSize: "12px" }}>Close</button>
      </div>
      
      <div className="xray-content" style={{ padding: "24px" }}>
        {/* Groundedness & Safety Section */}
        <section className="xray-section" style={{ marginBottom: "32px" }}>
          <span className="eyebrow" style={{ borderBottom: "1px solid var(--border)", paddingBottom: "4px", marginBottom: "16px" }}>Safety & Grounding</span>
          <div className="grid" style={{ gridTemplateColumns: "repeat(3, 1fr)", gap: "12px" }}>
            <div className="surface-card" style={{ padding: "12px", textAlign: "center", background: "var(--surface-muted)" }}>
              <span className="eyebrow" style={{ fontSize: "10px", marginBottom: "4px" }}>Grounded</span>
              <span className={`mono`} style={{ fontWeight: "700", color: safety?.groundedness?.score >= 0.7 ? "var(--success)" : "var(--danger)" }}>
                {safety?.groundedness?.score !== undefined ? (safety.groundedness.score * 100).toFixed(0) + "%" : "N/A"}
              </span>
            </div>
            <div className="surface-card" style={{ padding: "12px", textAlign: "center", background: "var(--surface-muted)" }}>
              <span className="eyebrow" style={{ fontSize: "10px", marginBottom: "4px" }}>Risk</span>
              <span className={`mono`} style={{ fontWeight: "700", color: safety?.injection_risk === "low" ? "var(--success)" : "var(--danger)" }}>
                {safety?.injection_risk?.toUpperCase() || "N/A"}
              </span>
            </div>
            <div className="surface-card" style={{ padding: "12px", textAlign: "center", background: "var(--surface-muted)" }}>
              <span className="eyebrow" style={{ fontSize: "10px", marginBottom: "4px" }}>Intent</span>
              <span className="mono" style={{ fontWeight: "700", fontSize: "12px" }}>{retrieval?.classification || "Baseline"}</span>
            </div>
          </div>
          {safety?.classifier_reason && (
            <div style={{ marginTop: "12px", fontSize: "12px", padding: "12px", background: "var(--warning-soft)", borderRadius: "var(--radius-md)", color: "var(--warning)" }}>
              {safety.classifier_reason}
            </div>
          )}
        </section>

        {/* Retrieval Transformations */}
        {retrieval?.transformations && (
          <section className="xray-section" style={{ marginBottom: "32px" }}>
            <span className="eyebrow" style={{ borderBottom: "1px solid var(--border)", paddingBottom: "4px", marginBottom: "16px" }}>Transformations</span>
            {retrieval.transformations.rewritten_query && (
              <div style={{ marginBottom: "16px" }}>
                <span className="eyebrow" style={{ fontSize: "11px", marginBottom: "6px" }}>Rewritten Query</span>
                <div style={{ padding: "12px", background: "var(--accent-soft)", borderRadius: "var(--radius-md)", fontSize: "13px", color: "var(--accent-strong)", fontWeight: "500" }}>
                  {retrieval.transformations.rewritten_query}
                </div>
              </div>
            )}
            {retrieval.transformations.expanded_queries?.length > 0 && (
              <div style={{ marginBottom: "16px" }}>
                <span className="eyebrow" style={{ fontSize: "11px", marginBottom: "6px" }}>Expansions</span>
                <ul style={{ margin: 0, padding: "0 0 0 16px", fontSize: "13px", color: "var(--text-secondary)" }}>
                  {retrieval.transformations.expanded_queries.map((q, i) => <li key={i} style={{ marginBottom: "4px" }}>{q}</li>)}
                </ul>
              </div>
            )}
            {retrieval.transformations.hyde_doc && (
              <div style={{ marginBottom: "16px" }}>
                <span className="eyebrow" style={{ fontSize: "11px", marginBottom: "6px" }}>HyDE Baseline</span>
                <div style={{ padding: "12px", background: "var(--surface-muted)", borderRadius: "var(--radius-md)", fontSize: "12px", maxHeight: "120px", overflowY: "auto", border: "1px solid var(--border)" }}>
                  {retrieval.transformations.hyde_doc}
                </div>
              </div>
            )}
          </section>
        )}

        {/* Strategy & Routing */}
        <section className="xray-section" style={{ marginBottom: "32px" }}>
          <span className="eyebrow" style={{ borderBottom: "1px solid var(--border)", paddingBottom: "4px", marginBottom: "16px" }}>Strategy</span>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span className="status-badge status-info" style={{ height: "28px", padding: "0 12px" }}>
              {retrieval?.routing?.selected_strategy?.toUpperCase() || "DEFAULT"}
            </span>
            {retrieval?.routing?.reason && (
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>{retrieval.routing.reason}</span>
            )}
          </div>
        </section>

        {/* Performance */}
        <section className="xray-section" style={{ marginBottom: "32px" }}>
          <span className="eyebrow" style={{ borderBottom: "1px solid var(--border)", paddingBottom: "4px", marginBottom: "16px" }}>Latency (ms)</span>
          <div className="grid" style={{ gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
            {Object.entries(retrieval?.execution_time_ms || {}).map(([key, val]) => (
              <div key={key} style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", padding: "4px 0", borderBottom: "1px dotted var(--border)" }}>
                <span style={{ color: "var(--text-secondary)", textTransform: "capitalize" }}>{key.replace(/_/g, " ")}</span>
                <span className="mono" style={{ fontWeight: "600" }}>{val}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Raw JSON */}
        <details>
          <summary style={{ cursor: "pointer", fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>RAW TRACE DATA</summary>
          <pre className="mono" style={{ fontSize: "11px", marginTop: "12px", padding: "16px", background: "#0B0D10", color: "#F7F7F5", borderRadius: "var(--radius-md)", overflowX: "auto" }}>
            {JSON.stringify(trace, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}
