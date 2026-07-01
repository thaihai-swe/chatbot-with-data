import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { getDocument, getChunkNote, upsertChunkNote, reindexDocument } from "../api/knowledgeApi";
import { useWorkspace } from "../context/WorkspaceContext";

const overlayStyle = {
  position: "fixed",
  inset: 0,
  background: "rgba(0,0,0,0.4)",
  zIndex: 999,
};

const drawerStyle = {
  position: "fixed",
  top: 0,
  right: 0,
  width: "60vw",
  height: "100vh",
  background: "var(--surface)",
  borderLeft: "1px solid var(--border)",
  boxShadow: "-4px 0 24px rgba(0,0,0,0.15)",
  zIndex: 1000,
  display: "flex",
  flexDirection: "column",
};

const headerStyle = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "20px 24px",
  borderBottom: "1px solid var(--border)",
};

const closeButtonStyle = {
  background: "none",
  border: "none",
  color: "var(--text-secondary)",
  cursor: "pointer",
  fontSize: "20px",
  padding: "4px 8px",
  borderRadius: "var(--radius-md)",
  lineHeight: 1,
};

const bodyStyle = {
  display: "flex",
  flex: 1,
  overflow: "hidden",
};

const leftPaneStyle = {
  width: "30%",
  borderRight: "1px solid var(--border)",
  overflowY: "auto",
  padding: "16px",
};

const rightPaneStyle = {
  width: "70%",
  overflowY: "auto",
  padding: "16px",
};

const chunkItemStyle = {
  padding: "10px 12px",
  borderRadius: "var(--radius-md)",
  marginBottom: "6px",
  cursor: "pointer",
  transition: "background 0.15s",
  fontSize: "13px",
};

const preStyle = {
  whiteSpace: "pre-wrap",
  wordBreak: "break-word",
  fontFamily: "var(--font-mono, monospace)",
  fontSize: "13px",
  lineHeight: 1.6,
  color: "var(--text-primary)",
  margin: 0,
};

function NoteEditor({ chunkId, onNoteChange }) {
  const [noteText, setNoteText] = useState("");
  const [noteLoading, setNoteLoading] = useState(false);
  const [noteSaved, setNoteSaved] = useState(false);

  useEffect(() => {
    if (!chunkId) return;
    setNoteLoading(true);
    getChunkNote(chunkId).then((data) => {
      setNoteText(data?.note_text || "");
    }).catch(() => {}).finally(() => setNoteLoading(false));
  }, [chunkId]);

  const handleSave = async () => {
    setNoteSaved(false);
    try {
      await upsertChunkNote(chunkId, noteText);
      setNoteSaved(true);
      if (onNoteChange) onNoteChange(chunkId, noteText);
      setTimeout(() => setNoteSaved(false), 2000);
    } catch (err) {
      alert("Failed to save note");
    }
  };

  return (
    <div style={{ marginTop: "12px" }}>
      <textarea
        style={{
          width: "100%",
          minHeight: "60px",
          padding: "8px 10px",
          fontSize: "12px",
          border: "1px solid var(--border)",
          borderRadius: "var(--radius-md)",
          background: "var(--surface)",
          color: "var(--text-primary)",
          resize: "vertical",
          fontFamily: "inherit",
        }}
        placeholder="Add a note..."
        value={noteText}
        onChange={(e) => setNoteText(e.target.value)}
        maxLength={2000}
        disabled={noteLoading}
      />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "4px" }}>
        <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>{noteText.length}/2000</span>
        <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
          {noteSaved && <span style={{ fontSize: "11px", color: "var(--accent-strong)" }}>Saved</span>}
          <button
            className="button button-primary"
            style={{ fontSize: "11px", padding: "2px 8px", height: "auto" }}
            onClick={handleSave}
            disabled={noteLoading}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

function ChunkModal({ chunk, documentTitle, onClose }) {
  if (!chunk) return null;

  return createPortal(
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: "680px" }}>
        <div className="modal-header">
          <h3 style={{ margin: 0, fontSize: "16px", fontWeight: 700 }}>
            {chunk.title || `Chunk`}
          </h3>
          <button 
            className="button button-ghost" 
            style={{ padding: 0, width: "32px", height: "32px", fontSize: "20px" }} 
            onClick={onClose}
          >
            &times;
          </button>
        </div>
        
        <div className="modal-body">
          <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "16px", marginBottom: "20px" }}>
            <div className="field">
              <span className="eyebrow" style={{ marginBottom: "4px" }}>Document</span>
              <span style={{ fontSize: "14px", fontWeight: "600" }}>{documentTitle || "Untitled Document"}</span>
            </div>
            {(chunk.page_number || chunk.metadata?.page_number) && (
              <div className="field">
                <span className="eyebrow" style={{ marginBottom: "4px" }}>Page</span>
                <span style={{ fontSize: "14px", fontWeight: "600" }}>{chunk.page_number || chunk.metadata.page_number}</span>
              </div>
            )}
          </div>

          <div className="field">
            <span className="eyebrow">Content</span>
            <div className="surface-card" style={{ padding: "16px", background: "var(--surface-muted)", fontSize: "14px", lineHeight: "1.6", whiteSpace: "pre-wrap", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)", maxHeight: "250px", overflowY: "auto" }}>
              {chunk.content || chunk.text || "No text content available."}
            </div>
          </div>

          <div className="field" style={{ marginTop: "16px" }}>
            <span className="eyebrow">Your Note</span>
            <NoteEditor chunkId={chunk.id} />
          </div>
        </div>
        
        <div className="modal-footer" style={{ borderTop: "1px solid var(--border)", paddingTop: "16px", display: "flex", justifyContent: "flex-end" }}>
          <button className="button button-primary" onClick={onClose}>Done</button>
        </div>
      </div>
    </div>,
    document.body
  );
}

function SourceBrowser({ documentId, onClose, inline }) {
  const { activeChunkId } = useWorkspace();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rechunking, setRechunking] = useState(false);
  const [selectedChunk, setSelectedChunk] = useState(null);
  const [popupChunk, setPopupChunk] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getDocument(documentId).then((data) => {
      if (cancelled) return;
      setDocument(data);
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [documentId]);

  const chunks = document?.chunks || [];

  useEffect(() => {
    if (activeChunkId && chunks.length > 0) {
      const index = chunks.findIndex((c) => c.id === activeChunkId);
      if (index !== -1) {
        setSelectedChunk(index);
        setTimeout(() => {
          const element = window.document.getElementById(`chunk-item-${activeChunkId}`);
          if (element) {
            element.scrollIntoView({ behavior: "smooth", block: "nearest" });
          }
        }, 50);
      }
    }
  }, [activeChunkId, chunks]);

  const handleRechunk = async () => {
    setRechunking(true);
    try {
      await reindexDocument(documentId);
      const data = await getDocument(documentId);
      setDocument(data);
    } catch {
      alert("Re-chunk failed. The document retains its previous chunks.");
    } finally {
      setRechunking(false);
    }
  };

  if (inline) {
    return (
      <div className="source-browser-inline" onClick={(e) => e.stopPropagation()}>
        <div style={headerStyle}>
          <h2 style={{ fontSize: "14px", margin: 0, color: "var(--text-primary)", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {document?.title || "Document"}
          </h2>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <button
              className="button button-ghost"
              style={{ height: "28px", padding: "0 8px", fontSize: "11px" }}
              type="button"
              disabled={rechunking}
              onClick={handleRechunk}
            >
              {rechunking ? "..." : "Re-chunk"}
            </button>
            <button style={{ ...closeButtonStyle, fontSize: "16px" }} onClick={onClose} type="button">
              ✕
            </button>
          </div>
        </div>
        {loading ? (
          <div style={{ flex: 1, display: "grid", placeItems: "center" }}>
            <div className="spinner" />
          </div>
        ) : (
          <div style={bodyStyle}>
            <div style={{ ...leftPaneStyle, width: "100%", borderRight: "none" }}>
              <h3 style={{ fontSize: "12px", fontWeight: 600, margin: "0 0 12px", color: "var(--text-secondary)" }}>
                Chunks ({chunks.length})
              </h3>
              {chunks.map((chunk, index) => (
                <div
                  key={chunk.id || index}
                  id={`chunk-item-${chunk.id || index}`}
                  style={{
                    ...chunkItemStyle,
                    padding: "12px 14px",
                    borderRadius: "var(--radius-md)",
                    marginBottom: "10px",
                    cursor: "pointer",
                    transition: "all var(--motion-base) var(--ease-standard)",
                    fontSize: "13px",
                    border: "1px solid var(--border)",
                    background:
                      selectedChunk === index
                        ? "rgba(99, 102, 241, 0.08)"
                        : "var(--surface)",
                    borderColor:
                      selectedChunk === index
                        ? "var(--accent-strong)"
                        : "var(--border)",
                    color:
                      selectedChunk === index
                        ? "var(--accent-strong)"
                        : "var(--text-primary)",
                  }}
                  onClick={() => {
                    setSelectedChunk(index);
                    setPopupChunk(chunk);
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: "13px" }}>{chunk.title || `Chunk ${index + 1}`}</div>
                  <div style={{ opacity: 0.6, fontSize: "11px", marginTop: "2px" }}>
                    Page {chunk.page_number ?? "?"}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {popupChunk && (
          <ChunkModal
            chunk={popupChunk}
            documentTitle={document?.title}
            onClose={() => setPopupChunk(null)}
          />
        )}
      </div>
    );
  }

  return (
    <>
      <div style={overlayStyle} onClick={onClose} />
      <div style={drawerStyle} onClick={(e) => e.stopPropagation()}>
        <div style={headerStyle}>
          <h2 style={{ fontSize: "16px", margin: 0, color: "var(--text-primary)" }}>
            {document?.title || "Document"}
          </h2>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <button
              className="button button-ghost"
              style={{ height: "32px", padding: "0 10px", fontSize: "12px" }}
              type="button"
              disabled={rechunking}
              onClick={handleRechunk}
            >
              {rechunking ? "Re-chunking..." : "Re-chunk"}
            </button>
            <button style={closeButtonStyle} onClick={onClose} type="button">
              ✕
            </button>
          </div>
        </div>
        {loading ? (
          <div style={{ flex: 1, display: "grid", placeItems: "center" }}>
            <div className="spinner" />
          </div>
        ) : (
          <div style={bodyStyle}>
            <div style={leftPaneStyle}>
              <h3 style={{ fontSize: "13px", fontWeight: 600, margin: "0 0 12px", color: "var(--text-secondary)" }}>
                Chunks ({chunks.length})
              </h3>
              {chunks.length === 0 && (
                <p style={{ fontSize: "13px", color: "var(--text-secondary)" }}>No chunks available</p>
              )}
              {chunks.map((chunk, index) => (
                <div
                  key={chunk.id || index}
                  id={`chunk-item-${chunk.id || index}`}
                  style={{
                    ...chunkItemStyle,
                    background:
                      selectedChunk === index
                        ? (activeChunkId && activeChunkId === chunk.id
                            ? "rgba(99, 102, 241, 0.12)"
                            : "var(--accent-strong)")
                        : "transparent",
                    color:
                      selectedChunk === index
                        ? (activeChunkId && activeChunkId === chunk.id
                            ? "var(--accent-strong)"
                            : "var(--text-on-accent, #fff)")
                        : "var(--text-primary)",
                    boxShadow:
                      selectedChunk === index && activeChunkId && activeChunkId === chunk.id
                        ? "inset 0 0 0 2px var(--accent-strong)"
                        : "none",
                  }}
                  onClick={() => setSelectedChunk(index)}
                >
                  <div style={{ fontWeight: 500 }}>{chunk.title || `Chunk ${index + 1}`}</div>
                  <div style={{ opacity: 0.6, fontSize: "11px", marginTop: "2px" }}>
                    Page {chunk.page_number ?? "?"} · Order {chunk.chunk_order ?? index + 1}
                  </div>
                </div>
              ))}
            </div>
            <div style={rightPaneStyle}>
              {selectedChunk !== null && chunks[selectedChunk]?.content ? (
                <>
                  <pre style={preStyle}>{chunks[selectedChunk].content}</pre>
                  <NoteEditor chunkId={chunks[selectedChunk].id} />
                </>
              ) : (
                <pre style={preStyle}>{document?.extracted_text || ""}</pre>
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default SourceBrowser;
