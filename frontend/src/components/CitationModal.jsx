import React from "react";

export default function CitationModal({ citation, chunk, onClose }) {
  if (!citation || !chunk) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Citation Source</h3>
          <button className="button button-ghost" style={{ padding: "0", width: "32px", height: "32px", fontSize: "20px" }} onClick={onClose}>&times;</button>
        </div>
        
        <div className="modal-body">
          <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "16px", marginBottom: "24px" }}>
            <div className="field">
              <span className="eyebrow" style={{ marginBottom: "4px" }}>Document</span>
              <span style={{ fontSize: "14px", fontWeight: "600" }}>{chunk.title || chunk.metadata?.title || "Untitled Document"}</span>
            </div>
            <div className="field">
              <span className="eyebrow" style={{ marginBottom: "4px" }}>Relevance</span>
              <span className={`status-badge status-success`} style={{ width: "fit-content" }}>
                {((chunk.similarity_score || chunk.score || 0) * 100).toFixed(1)}%
              </span>
            </div>
            {(chunk.page_number || chunk.metadata?.page_number) && (
              <div className="field">
                <span className="eyebrow" style={{ marginBottom: "4px" }}>Page</span>
                <span style={{ fontSize: "14px", fontWeight: "600" }}>{chunk.page_number || chunk.metadata.page_number}</span>
              </div>
            )}
          </div>

          <div className="field">
            <span className="eyebrow">Excerpt</span>
            <div className="surface-card" style={{ padding: "16px", background: "var(--surface-muted)", fontSize: "15px", lineHeight: "1.6", whiteSpace: "pre-wrap", border: "1px solid var(--border)" }}>
              {chunk.text || chunk.content || chunk.metadata?.text || "No text content available."}
            </div>
          </div>

          {(chunk.parent_text || chunk.metadata?.parent_text) && (
            <div className="field" style={{ marginTop: "16px" }}>
              <span className="eyebrow">Extended Context</span>
              <div className="surface-card" style={{ padding: "16px", fontSize: "14px", color: "var(--text-secondary)", borderLeft: "3px solid var(--accent)" }}>
                {chunk.parent_text || chunk.metadata.parent_text}
              </div>
            </div>
          )}
          
          <div style={{ marginTop: "24px", fontSize: "11px", color: "var(--text-muted)" }} className="mono">
            ID: {chunk.chunk_id}
          </div>
        </div>
        
        <div className="modal-footer">
          <button className="button button-primary" onClick={onClose}>Done</button>
        </div>
      </div>
    </div>
  );
}
