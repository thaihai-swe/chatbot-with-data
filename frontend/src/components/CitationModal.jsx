import React from "react";

export default function CitationModal({ citation, chunk, onClose }) {
  if (!citation || !chunk) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Citation Details</h3>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>
        
        <div className="modal-body">
          <div className="citation-meta-grid">
            <div className="meta-item">
              <span className="label">Document</span>
              <span className="value">{chunk.title || chunk.metadata?.title || "Untitled Document"}</span>
            </div>
            <div className="meta-item">
              <span className="label">Score</span>
              <span className={`value mono ${(chunk.similarity_score || chunk.score || 0) > 0.7 ? "text-success" : ""}`}>
                {(chunk.similarity_score || chunk.score || 0).toFixed(4)}
              </span>
            </div>
            {(chunk.page_number || chunk.metadata?.page_number) && (
              <div className="meta-item">
                <span className="label">Page</span>
                <span className="value">{chunk.page_number || chunk.metadata.page_number}</span>
              </div>
            )}
            {(chunk.source_url || chunk.metadata?.source_url) && (
              <div className="meta-item">
                <span className="label">Source</span>
                <a href={chunk.source_url || chunk.metadata.source_url} target="_blank" rel="noopener noreferrer" className="value link">
                  View Original
                </a>
              </div>
            )}
          </div>

          <div className="chunk-text-container">
            <h4>Retrieved Chunk Text</h4>
            <div className="chunk-text">
              {chunk.text || chunk.content || chunk.metadata?.text || "No text content available."}
            </div>
          </div>

          {(chunk.parent_text || chunk.metadata?.parent_text) && (
            <div className="chunk-text-container" style={{ marginTop: "20px" }}>
              <h4>Parent Context</h4>
              <div className="chunk-text parent-context">
                {chunk.parent_text || chunk.metadata.parent_text}
              </div>
            </div>
          )}
          
          <div style={{ marginTop: "20px", fontSize: "0.7rem", opacity: 0.5 }} className="mono">
            Chunk ID: {chunk.chunk_id}
          </div>
        </div>
        
        <div className="modal-footer">
          <button className="button" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
}
