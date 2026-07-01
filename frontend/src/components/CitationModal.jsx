import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { getChunkNote, upsertChunkNote } from "../api/knowledgeApi";

function getQuoteText(citation) {
  return citation?.quote_text || citation?.metadata?.quote_text || null;
}

export default function CitationModal({ citation, chunk, onClose }) {
  const [showFullContext, setShowFullContext] = useState(false);
  const [noteText, setNoteText] = useState("");
  const [noteLoading, setNoteLoading] = useState(false);
  const [noteSaved, setNoteSaved] = useState(false);

  useEffect(() => {
    if (!chunk?.chunk_id) return;
    setNoteLoading(true);
    getChunkNote(chunk.chunk_id).then((data) => {
      if (data) {
        setNoteText(data.note_text || "");
      } else {
        setNoteText("");
      }
    }).catch(() => {}).finally(() => setNoteLoading(false));
  }, [chunk?.chunk_id]);

  if (!citation || !chunk) return null;

  const quoteText = getQuoteText(citation);

  const handleSaveNote = async () => {
    setNoteSaved(false);
    try {
      await upsertChunkNote(chunk.chunk_id, noteText);
      setNoteSaved(true);
      setTimeout(() => setNoteSaved(false), 2000);
    } catch (err) {
      alert("Failed to save note");
    }
  };

  return createPortal(
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
            <span className="eyebrow">{quoteText ? "Quote" : "Excerpt"}</span>
            {quoteText ? (
              <div className="quote-highlight" style={{ padding: "16px", fontSize: "15px", lineHeight: "1.6", fontStyle: "italic", borderLeft: "3px solid var(--accent)", background: "var(--surface-muted)" }}>
                &ldquo;{quoteText}&rdquo;
              </div>
            ) : (
              <div className="surface-card" style={{ padding: "16px", background: "var(--surface-muted)", fontSize: "15px", lineHeight: "1.6", whiteSpace: "pre-wrap", border: "1px solid var(--border)" }}>
                {chunk.text || chunk.content || chunk.metadata?.text || "No text content available."}
              </div>
            )}
          </div>

          {quoteText && (
            <div className="field" style={{ marginTop: "16px" }}>
              <button
                className="button button-ghost"
                style={{ fontSize: "12px", padding: "4px 8px", cursor: "pointer" }}
                onClick={() => setShowFullContext(!showFullContext)}
              >
                {showFullContext ? "Hide full context" : "Show full context"}
              </button>
              {showFullContext && (
                <div className="surface-card" style={{ marginTop: "8px", padding: "16px", background: "var(--surface-muted)", fontSize: "15px", lineHeight: "1.6", whiteSpace: "pre-wrap", border: "1px solid var(--border)" }}>
                  {chunk.text || chunk.content || chunk.metadata?.text || "No text content available."}
                </div>
              )}
            </div>
          )}

          <div className="field" style={{ marginTop: "16px" }}>
            <span className="eyebrow">Your Note</span>
            <textarea
              style={{
                width: "100%",
                minHeight: "80px",
                padding: "10px 12px",
                fontSize: "13px",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-md)",
                background: "var(--surface)",
                color: "var(--text-primary)",
                resize: "vertical",
                fontFamily: "inherit",
                marginTop: "6px",
              }}
              placeholder="Add a note about this source..."
              value={noteText}
              onChange={(e) => setNoteText(e.target.value)}
              maxLength={2000}
              disabled={noteLoading}
            />
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "6px" }}>
              <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                {noteText.length}/2000
              </span>
              <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                {noteSaved && (
                  <span style={{ fontSize: "12px", color: "var(--accent-strong)" }}>Saved</span>
                )}
                <button
                  className="button button-primary"
                  style={{ fontSize: "12px", padding: "4px 12px", height: "auto" }}
                  onClick={handleSaveNote}
                  disabled={noteLoading}
                >
                  Save Note
                </button>
              </div>
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
    </div>,
    document.body
  );
}
