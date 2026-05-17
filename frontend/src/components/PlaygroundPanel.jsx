import React, { useState } from "react";

export default function PlaygroundPanel({ 
  panelId, 
  config, 
  onConfigChange, 
  result, 
  isLoading, 
  otherPanelChunks = [] 
}) {
  const [showConfig, setShowConfig] = useState(true);

  const toggleField = (field) => {
    onConfigChange({ ...config, [field]: !config[field] });
  };

  const setMode = (mode) => {
    onConfigChange({ ...config, retrieval_mode: mode });
  };

  const isMatched = (chunkId) => {
    return otherPanelChunks.some(c => c.chunk_id === chunkId);
  };

  return (
    <div className="panel" style={{ display: "flex", flexDirection: "column", height: "100%", padding: "0", overflow: "hidden" }}>
      <div className="panel-header" style={{ padding: "24px 32px", borderBottom: "1px solid var(--border)", background: "var(--surface-muted)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ fontSize: "18px", fontWeight: "750" }}>Strategy {panelId}</h3>
          <button 
            onClick={() => setShowConfig(!showConfig)} 
            className="button button-ghost"
            style={{ fontSize: "12px", height: "32px", padding: "0 12px" }}
          >
            {showConfig ? "Hide Config" : "Show Config"}
          </button>
        </div>
      </div>

      {showConfig && (
        <div style={{ padding: "24px 32px", borderBottom: "1px solid var(--border)" }}>
          <div className="field" style={{ marginBottom: "20px" }}>
            <span style={{ fontSize: "12px", textTransform: "uppercase", color: "var(--text-muted)", marginBottom: "8px" }}>Retrieval Mode</span>
            <div style={{ display: "flex", gap: "4px", background: "var(--surface-muted)", padding: "4px", borderRadius: "var(--radius-md)" }}>
              {["semantic", "keyword", "hybrid"].map(mode => (
                <button
                  key={mode}
                  style={{ 
                    flex: 1, 
                    height: "32px", 
                    fontSize: "12px", 
                    borderRadius: "var(--radius-sm)",
                    border: "none",
                    cursor: "pointer",
                    background: config.retrieval_mode === mode ? "var(--surface)" : "transparent",
                    color: config.retrieval_mode === mode ? "var(--text-primary)" : "var(--text-secondary)",
                    boxShadow: config.retrieval_mode === mode ? "var(--shadow-xs)" : "none",
                    fontWeight: config.retrieval_mode === mode ? "700" : "500",
                    transition: "all 0.2s"
                  }}
                  onClick={() => setMode(mode)}
                >
                  {mode.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <label className="config-toggle" style={{ padding: "4px 0" }}>
              <input type="checkbox" checked={config.enable_hyde} onChange={() => toggleField("enable_hyde")} />
              <span>HyDE</span>
            </label>
            <label className="config-toggle" style={{ padding: "4px 0" }}>
              <input type="checkbox" checked={config.enable_expansion} onChange={() => toggleField("enable_expansion")} />
              <span>Expansion</span>
            </label>
            <label className="config-toggle" style={{ padding: "4px 0" }}>
              <input type="checkbox" checked={config.enable_reranking} onChange={() => toggleField("enable_reranking")} />
              <span>Reranking</span>
            </label>
            <label className="config-toggle" style={{ padding: "4px 0" }}>
              <input type="checkbox" checked={config.enable_parent_child} onChange={() => toggleField("enable_parent_child")} />
              <span>Parent-Child</span>
            </label>
          </div>
        </div>
      )}

      <div style={{ flex: 1, overflowY: "auto", padding: "32px" }}>
        {isLoading && (
          <div className="empty-state">
            <div className="spinner" style={{ marginBottom: "20px" }}></div>
            <p className="mono" style={{ fontSize: "13px" }}>Synthesizing strategy...</p>
          </div>
        )}

        {!isLoading && result && (
          <div className="stack" style={{ gap: "32px" }}>
            <div>
              <span className="eyebrow">Assistant Response</span>
              <div style={{ fontSize: "15px", lineHeight: "1.7", color: "var(--text-primary)", whiteSpace: "pre-wrap" }}>
                {result.answer || "No response generated."}
              </div>
            </div>

            <div>
              <span className="eyebrow">Retrieved Context ({result.chunks?.length || 0})</span>
              <div className="stack" style={{ gap: "12px", marginTop: "12px" }}>
                {result.chunks?.map((chunk, idx) => {
                  const matched = isMatched(chunk.chunk_id);
                  return (
                    <div key={idx} className="surface-card" style={{ 
                      padding: "16px", 
                      fontSize: "13px", 
                      background: matched ? "var(--accent-soft)" : "var(--surface)",
                      border: matched ? "1px solid var(--accent)" : "1px solid var(--border)",
                      opacity: matched ? 1 : 0.8
                    }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                        <span className="mono" style={{ fontSize: "11px", fontWeight: "700" }}>CHUNK {chunk.chunk_id.slice(0, 8)}</span>
                        {matched && <span className="status-badge status-info" style={{ height: "18px", fontSize: "10px" }}>MATCHED</span>}
                        <span className="mono" style={{ fontSize: "11px", opacity: 0.6 }}>SCORE: {(chunk.similarity_score || 0).toFixed(4)}</span>
                      </div>
                      <div style={{ color: "var(--text-secondary)", lineHeight: "1.5" }}>
                        {chunk.text?.slice(0, 160)}...
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {!isLoading && !result && (
          <div className="empty-state">
            <p style={{ fontSize: "14px", color: "var(--text-muted)" }}>Select a strategy and run comparison to begin analysis.</p>
          </div>
        )}
      </div>
    </div>
  );
}
