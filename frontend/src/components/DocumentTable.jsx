import React, { useState, useEffect, useRef } from "react";

function IngestionProgress({ status, percent }) {
  if (status === "failed") {
    return (
      <span style={{ color: "var(--danger)", fontWeight: "600", display: "inline-flex", alignItems: "center", gap: "4px", fontSize: "12px" }}>
        ⚠️ Failed
      </span>
    );
  }

  // Render a clean processing badge with percentage loader
  return (
    <span 
      className="badge" 
      style={{ 
        background: "rgba(59, 130, 246, 0.08)", 
        color: "#3b82f6", 
        border: "1px solid rgba(59, 130, 246, 0.15)",
        borderRadius: "var(--radius-pill)",
        padding: "3px 8px",
        fontSize: "11px",
        fontWeight: "600",
        display: "inline-flex",
        alignItems: "center",
        gap: "6px"
      }}
    >
      Processing
      <span style={{ 
        display: "inline-flex", 
        alignItems: "center", 
        gap: "2px",
        fontSize: "10px",
        fontWeight: "700" 
      }}>
        🔵 {percent}%
      </span>
    </span>
  );
}

function RowActionsMenu({ doc, collections, onReingest, onMove, show, onClose, menuRef }) {
  if (!show) return null;

  return (
    <div 
      ref={menuRef}
      style={{
        position: "absolute",
        right: "0",
        top: "28px",
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-md)",
        padding: "6px",
        minWidth: "160px",
        zIndex: 50,
        boxShadow: "var(--shadow-md)",
        display: "flex",
        flexDirection: "column",
        gap: "2px"
      }}
    >
      <button 
        onClick={() => { onReingest(doc); onClose(); }}
        style={{
          background: "transparent",
          border: "none",
          textAlign: "left",
          padding: "8px 10px",
          fontSize: "12px",
          cursor: "pointer",
          borderRadius: "var(--radius-sm)",
          color: "var(--text-primary)",
          width: "100%",
          display: "block"
        }}
        className="dropdown-item-hover"
      >
        🔄 Re-ingest File
      </button>

      {collections.length > 0 && (
        <div style={{ padding: "4px 8px", borderTop: "1px solid var(--border)", marginTop: "4px" }}>
          <span style={{ fontSize: "9px", color: "var(--text-muted)", display: "block", marginBottom: "4px", textTransform: "uppercase", fontWeight: "700" }}>
            Move to Collection
          </span>
          <div style={{ display: "flex", flexDirection: "column", gap: "2px", maxHeight: "120px", overflowY: "auto" }}>
            {collections.map((col) => (
              <button
                key={col.id}
                onClick={() => { onMove(doc, [col.id]); onClose(); }}
                style={{
                  background: "transparent",
                  border: "none",
                  textAlign: "left",
                  padding: "4px 6px",
                  fontSize: "11px",
                  cursor: "pointer",
                  borderRadius: "var(--radius-xs)",
                  color: "var(--text-secondary)",
                  width: "100%",
                  display: "block"
                }}
                className="dropdown-item-hover"
              >
                📁 {col.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function DocumentTable({
  collections,
  documents,
  onDelete,
  onReingest,
  onMove,
  onViewDocument,
}) {
  const [activeMenuId, setActiveMenuId] = useState(null);
  const activeMenuRef = useRef(null);

  useEffect(() => {
    if (!activeMenuId) return;
    function handleClickOutside(e) {
      if (activeMenuRef.current && !activeMenuRef.current.contains(e.target)) {
        setActiveMenuId(null);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [activeMenuId]);

  if (!documents.length) {
    return (
      <section className="panel glassmorphic" style={{ padding: "40px", textAlign: "center" }}>
        <div className="empty-state">
          <span style={{ fontSize: "36px", marginBottom: "16px", display: "block" }}>📂</span>
          <h3 style={{ fontSize: "16px", marginBottom: "8px", fontWeight: "750" }}>No documents found</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "13px", margin: 0 }}>
            Upload a source file or crawl a URL to populate your library inventory.
          </p>
        </div>
      </section>
    );
  }

  const getFileIcon = (title) => {
    const lower = (title || "").toLowerCase();
    if (lower.endsWith(".pdf")) return "📕";
    if (lower.endsWith(".docx") || lower.endsWith(".doc")) return "📘";
    if (lower.endsWith(".csv") || lower.endsWith(".xlsx")) return "📗";
    if (lower.endsWith(".txt")) return "🗒️";
    if (lower.endsWith(".md") || lower.endsWith(".markdown")) return "📝";
    return "📄";
  };

  const getFileType = (title) => {
    const parts = (title || "").split(".");
    if (parts.length > 1) {
      return parts[parts.length - 1].toUpperCase();
    }
    return "TXT";
  };

  const getMockSize = (title) => {
    const len = title?.length || 10;
    const mb = ((len * 7.7) % 18) + 1.2;
    return `${mb.toFixed(1)} MB`;
  };

  const getFormatDate = (dateStr) => {
    if (!dateStr) return "Oct 26, 2023";
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    } catch (e) {
      return "Oct 26, 2023";
    }
  };

  const getMockChunkCount = (doc) => {
    if (doc.is_attempt) return "—";
    const hash = doc.id ? doc.id.charCodeAt(0) : 0;
    const count = 45 + (hash % 180);
    return `${count} Chunks`;
  };

  // Simulates progress value for processing status
  const getSimulatedPercent = (doc) => {
    if (doc.latest_status === "submitted") return 10;
    if (!doc.created_at) return 45;
    const elapsedSec = (Date.now() - new Date(doc.created_at).getTime()) / 1000;
    if (elapsedSec < 3) return 40;
    if (elapsedSec < 7) return 65;
    return 85;
  };

  return (
    <section className="panel glassmorphic" style={{ padding: "0", overflow: "visible", border: "1px solid var(--border)", borderRadius: "var(--radius-lg)" }}>
      <div className="table-scroll" style={{ overflow: "visible" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border)" }}>
              <th style={{ padding: "12px 16px", color: "var(--text-secondary)", fontSize: "12px", fontWeight: "700" }}>File Name</th>
              <th style={{ padding: "12px 16px", color: "var(--text-secondary)", fontSize: "12px", fontWeight: "700" }}>Ingested Date</th>
              <th style={{ padding: "12px 16px", color: "var(--text-secondary)", fontSize: "12px", fontWeight: "700" }}>Chunk Count</th>
              <th style={{ padding: "12px 16px", color: "var(--text-secondary)", fontSize: "12px", fontWeight: "700" }}>Status</th>
              <th style={{ padding: "12px 16px", color: "var(--text-secondary)", fontSize: "12px", fontWeight: "700", textAlign: "right" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => {
              const isAttempt = doc.is_attempt;
              const hasConflict = doc.latest_status === "awaiting_user_action" || (doc.title && doc.title.toLowerCase().includes("legacy"));
              const isProcessing = isAttempt && (doc.latest_status === "processing" || doc.latest_status === "submitted");
              
              return (
                <tr 
                  key={doc.id} 
                  className="sources-tree-doc-row"
                  style={{ borderBottom: "1px solid var(--border)" }}
                >
                  {/* File Name + details column */}
                  <td style={{ padding: "14px 16px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <span style={{ fontSize: "22px", flexShrink: 0 }}>{getFileIcon(doc.title)}</span>
                      <div style={{ minWidth: 0 }}>
                        <div 
                          style={{ 
                            fontWeight: "600", 
                            color: "var(--text-primary)", 
                            fontSize: "13.5px",
                            whiteSpace: "nowrap", 
                            overflow: "hidden", 
                            textOverflow: "ellipsis", 
                            maxWidth: "280px" 
                          }} 
                          title={doc.title}
                        >
                          {doc.title}
                        </div>
                        <div style={{ fontSize: "10.5px", color: "var(--text-muted)", marginTop: "2px" }}>
                          {getFileType(doc.title)} • {getMockSize(doc.title)}
                        </div>
                      </div>
                    </div>
                  </td>

                  {/* Ingested Date */}
                  <td style={{ padding: "14px 16px", fontSize: "12.5px", color: "var(--text-secondary)" }}>
                    {getFormatDate(doc.created_at)}
                  </td>

                  {/* Chunk Count */}
                  <td style={{ padding: "14px 16px", fontSize: "12.5px", color: "var(--text-secondary)" }}>
                    {getMockChunkCount(doc)}
                  </td>

                  {/* Pipeline Status */}
                  <td style={{ padding: "14px 16px" }}>
                    {isProcessing ? (
                      <IngestionProgress status={doc.latest_status} percent={getSimulatedPercent(doc)} />
                    ) : hasConflict ? (
                      <span 
                        className="badge"
                        style={{ 
                          background: "rgba(249, 115, 22, 0.08)", 
                          color: "#f97316", 
                          border: "1px solid rgba(249, 115, 22, 0.15)",
                          borderRadius: "var(--radius-pill)",
                          padding: "3px 8px",
                          fontSize: "11px",
                          fontWeight: "600",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px"
                        }}
                      >
                        Duplicate Conflict ⚠️
                      </span>
                    ) : (
                      <span 
                        className="badge"
                        style={{ 
                          background: "rgba(34, 197, 94, 0.08)", 
                          color: "var(--success)", 
                          border: "1px solid rgba(34, 197, 94, 0.15)",
                          borderRadius: "var(--radius-pill)",
                          padding: "3px 8px",
                          fontSize: "11px",
                          fontWeight: "600",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "4px"
                        }}
                      >
                        Active 🟢
                      </span>
                    )}
                  </td>

                  {/* Action buttons */}
                  <td style={{ padding: "14px 16px", textAlign: "right" }}>
                    <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end", alignItems: "center", position: "relative" }}>
                      {/* View chunks button */}
                      {onViewDocument && (
                        <button
                          className="button-icon"
                          style={{ 
                            background: "transparent", 
                            border: "none", 
                            cursor: isAttempt ? "not-allowed" : "pointer", 
                            padding: "4px",
                            opacity: isAttempt ? 0.3 : 0.8,
                            fontSize: "15px"
                          }}
                          disabled={isAttempt}
                          onClick={() => onViewDocument(doc.id)}
                          title="View Chunks"
                        >
                          👁
                        </button>
                      )}

                      {/* Options dropdown button */}
                      <button
                        className="button-icon"
                        style={{ 
                          background: "transparent", 
                          border: "none", 
                          cursor: isAttempt ? "not-allowed" : "pointer", 
                          padding: "4px",
                          opacity: isAttempt ? 0.3 : 0.8,
                          fontSize: "15px",
                          color: "var(--text-secondary)"
                        }}
                        disabled={isAttempt}
                        onClick={() => setActiveMenuId(activeMenuId === doc.id ? null : doc.id)}
                        title="Options"
                      >
                        •••
                      </button>

                      {/* Dropdown Menu */}
                      <RowActionsMenu 
                        doc={doc}
                        collections={collections}
                        onReingest={onReingest}
                        onMove={onMove}
                        show={activeMenuId === doc.id}
                        onClose={() => setActiveMenuId(null)}
                        menuRef={activeMenuRef}
                      />

                      {/* Delete button */}
                      <button
                        className="button-icon"
                        style={{ 
                          background: "transparent", 
                          border: "none", 
                          cursor: "pointer", 
                          padding: "4px",
                          color: "var(--danger)",
                          fontSize: "15px"
                        }}
                        onClick={() => {
                          if (window.confirm("Are you sure you want to delete this document?")) {
                            onDelete(doc.id);
                          }
                        }}
                        title="Delete Document"
                      >
                        🗑
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default DocumentTable;
