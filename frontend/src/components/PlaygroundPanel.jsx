import React, { useState } from "react";
import StatusBadge from "./StatusBadge";

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
    <div className="playground-panel glass">
      <div className="panel-header">
        <h3>Strategy {panelId}</h3>
        <button 
          onClick={() => setShowConfig(!showConfig)} 
          className="button button-outline"
          style={{ fontSize: "0.7rem", padding: "4px 8px" }}
        >
          {showConfig ? "Hide Config" : "Show Config"}
        </button>
      </div>

      {showConfig && (
        <div className="panel-config">
          <div className="config-group">
            <label className="label-small">Retrieval Mode</label>
            <div className="mode-selector">
              {["semantic", "keyword", "hybrid"].map(mode => (
                <button
                  key={mode}
                  className={`mode-button ${config.retrieval_mode === mode ? "active" : ""}`}
                  onClick={() => setMode(mode)}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>

          <div className="config-grid">
            <label className="config-toggle">
              <input type="checkbox" checked={config.enable_hyde} onChange={() => toggleField("enable_hyde")} />
              <span>HyDE</span>
            </label>
            <label className="config-toggle">
              <input type="checkbox" checked={config.enable_expansion} onChange={() => toggleField("enable_expansion")} />
              <span>Expansion</span>
            </label>
            <label className="config-toggle">
              <input type="checkbox" checked={config.enable_reranking} onChange={() => toggleField("enable_reranking")} />
              <span>Reranking</span>
            </label>
            <label className="config-toggle">
              <input type="checkbox" checked={config.enable_parent_child} onChange={() => toggleField("enable_parent_child")} />
              <span>Parent-Child</span>
            </label>
          </div>
        </div>
      )}

      <div className="panel-results">
        {isLoading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Retrieving & Generating...</p>
          </div>
        )}

        {!isLoading && result && (
          <>
            <div className="result-answer">
              <h4>Answer</h4>
              <div className="answer-text">{result.answer || "No answer generated."}</div>
            </div>

            <div className="result-chunks">
              <h4>Retrieved Chunks ({result.chunks?.length || 0})</h4>
              <div className="chunks-list-playground">
                {result.chunks?.map((chunk, idx) => {
                  const matched = isMatched(chunk.chunk_id);
                  return (
                    <div key={idx} className={`mini-chunk glass ${matched ? "chunk-matched" : "chunk-unique"}`}>
                      <div className="chunk-header-mini">
                        <span className="mono" style={{ fontSize: "0.6rem" }}>{chunk.chunk_id.slice(0, 8)}</span>
                        {matched && <span className="matched-badge">Matched</span>}
                        <span className="score-badge">{(chunk.similarity_score || 0).toFixed(3)}</span>
                      </div>
                      <div className="chunk-content-mini">
                        {chunk.text?.slice(0, 150)}...
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}

        {!isLoading && !result && (
          <div className="empty-state">
            <p>Configure strategy and click "Run Comparison" to see results.</p>
          </div>
        )}
      </div>
    </div>
  );
}
