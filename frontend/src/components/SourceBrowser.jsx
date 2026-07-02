import { useEffect, useState, useMemo, useRef } from "react";
import { createPortal } from "react-dom";
import { getDocument, getChunkNote, upsertChunkNote, reindexDocument } from "../api/knowledgeApi";
import { useWorkspace } from "../context/WorkspaceContext";

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

  const handleSave = async (e) => {
    e.stopPropagation(); // Avoid triggering card selection on button click
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

  const accentColor = "#00d992"; // Electric green

  return (
    <div style={{ marginTop: "14px", borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: "12px" }} onClick={e => e.stopPropagation()}>
      <label style={{ fontSize: "10px", fontWeight: "750", color: "rgba(255,255,255,0.4)", textTransform: "uppercase", display: "block", marginBottom: "6px" }}>
        Notes Editor
      </label>
      <textarea
        style={{
          width: "100%",
          minHeight: "74px",
          padding: "8px 12px",
          fontSize: "12px",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: "var(--radius-sm)",
          background: "#0a0a0a",
          color: "rgba(255,255,255,0.9)",
          resize: "none",
          fontFamily: "inherit",
          lineHeight: "1.4",
          outline: "none"
        }}
        placeholder="Add metadata tags or notes..."
        value={noteText}
        onChange={(e) => setNoteText(e.target.value)}
        maxLength={2000}
        disabled={noteLoading}
      />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "6px" }}>
        <span style={{ fontSize: "10px", color: "rgba(255,255,255,0.4)" }}>{noteText.length}/2000</span>
        <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
          {noteSaved && <span style={{ fontSize: "11px", color: accentColor, fontWeight: "600" }}>Saved</span>}
          <button
            type="button"
            style={{ 
              fontSize: "10.5px", 
              padding: "0 12px", 
              height: "26px",
              background: accentColor,
              color: "black",
              fontWeight: "750",
              border: "none",
              cursor: "pointer",
              borderRadius: "var(--radius-xs)"
            }}
            onClick={handleSave}
            disabled={noteLoading}
          >
            Save Notes
          </button>
        </div>
      </div>
    </div>
  );
}

export default function SourceBrowser({ documentId, onClose, inline }) {
  const { activeChunkId } = useWorkspace();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rechunking, setRechunking] = useState(false);
  
  // Interaction Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState("similarity"); // similarity, length
  const [selectedChunkIndex, setSelectedChunkIndex] = useState(0);

  const containerRef = useRef(null);

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

  const rawChunks = document?.chunks || [];

  // Sort and Filter Chunks List
  const filteredChunks = useMemo(() => {
    let result = [...rawChunks];
    
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      result = result.filter(c => (c.content || c.text || "").toLowerCase().includes(q));
    }

    if (sortBy === "similarity") {
      result.sort((a, b) => {
        const simA = ((a.content || "").length * 3) % 40 / 100 + 0.60;
        const simB = ((b.content || "").length * 3) % 40 / 100 + 0.60;
        return simB - simA;
      });
    } else if (sortBy === "length") {
      result.sort((a, b) => (b.content || "").length - (a.content || "").length);
    }

    return result;
  }, [rawChunks, searchQuery, sortBy]);

  useEffect(() => {
    if (activeChunkId && filteredChunks.length > 0) {
      const idx = filteredChunks.findIndex((c) => c.id === activeChunkId);
      if (idx !== -1) {
        setSelectedChunkIndex(idx);
      }
    }
  }, [activeChunkId, filteredChunks]);

  const handleRechunk = async () => {
    setRechunking(true);
    try {
      await reindexDocument(documentId);
      const data = await getDocument(documentId);
      setDocument(data);
      setSelectedChunkIndex(0);
    } catch {
      alert("Re-chunk failed. The document retains its previous chunks.");
    } finally {
      setRechunking(false);
    }
  };

  const activeChunkText = filteredChunks[selectedChunkIndex]?.content || filteredChunks[selectedChunkIndex]?.text || "";
  const rawDocumentText = document?.extracted_text || rawChunks.map(c => c.content || c.text).join("\n\n");

  const documentLines = useMemo(() => {
    if (!rawDocumentText) return [];
    return rawDocumentText.split("\n");
  }, [rawDocumentText]);

  // Clean title tags from chunks and find correct line indexes
  const activeLineRange = useMemo(() => {
    if (!activeChunkText || documentLines.length === 0 || !rawDocumentText) {
      return { start: -1, end: -1 };
    }
    
    const cleanChunk = activeChunkText.replace(/^\[[^\]]+\]\s*/, '').trim();
    if (!cleanChunk) return { start: -1, end: -1 };

    const cleanChunkNorm = cleanChunk.replace(/\s+/g, ' ').toLowerCase();
    const searchAnchor = cleanChunkNorm.slice(0, 45); // match first 45 characters

    const cleanDocNorm = rawDocumentText.replace(/\s+/g, ' ').toLowerCase();
    const matchOffset = cleanDocNorm.indexOf(searchAnchor);

    if (matchOffset === -1) return { start: -1, end: -1 };

    let currentNormOffset = 0;
    let startLine = -1;
    for (let i = 0; i < documentLines.length; i++) {
      const lineNorm = documentLines[i].replace(/\s+/g, ' ').toLowerCase();
      if (startLine === -1 && (currentNormOffset + lineNorm.length >= matchOffset)) {
        startLine = i;
      }
      currentNormOffset += lineNorm.length + 1; // +1 accounts for line breaks
    }

    if (startLine === -1) return { start: -1, end: -1 };

    let endLine = startLine;
    let accumulatedLength = 0;
    while (endLine < documentLines.length && accumulatedLength < cleanChunk.length) {
      accumulatedLength += documentLines[endLine].length + 1;
      endLine++;
    }

    return { start: startLine, end: Math.max(startLine, endLine - 1) };
  }, [documentLines, activeChunkText, rawDocumentText]);

  // Scroll active lines into view within the scrollable container ref
  useEffect(() => {
    if (activeLineRange.start !== -1 && containerRef.current) {
      setTimeout(() => {
        const el = window.document.getElementById(`doc-line-${activeLineRange.start}`);
        if (el) {
          el.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }, 80);
    }
  }, [activeLineRange]);

  const getMockSimilarity = (chunkText) => {
    const len = chunkText?.length || 10;
    const sim = ((len * 3) % 10) / 100 + 0.90;
    return sim.toFixed(3);
  };

  const accentColor = "#00d992"; // Electric green

  const contentElement = (
    <div 
      style={{ 
        width: inline ? "100%" : "92vw", 
        height: inline ? "100%" : "90vh", 
        display: "flex", 
        flexDirection: "column",
        overflow: "hidden",
        borderRadius: inline ? "0" : "var(--radius-lg)",
        boxShadow: inline ? "none" : "0 20px 50px rgba(0,0,0,0.6)",
        background: "#0c0d0f",
        border: "1px solid rgba(255,255,255,0.08)"
      }}
    >
      
      {/* Top Header Controls Row - Explicit background color to prevent transparency issues */}
      <div 
        style={{ 
          padding: "16px 24px", 
          background: "#0e1013",
          borderBottom: "1px solid rgba(255,255,255,0.08)", 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "center", 
          flexWrap: "wrap",
          gap: "16px" 
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px", minWidth: 0 }}>
          <span style={{ fontSize: "20px" }}>📄</span>
          <h2 style={{ fontSize: "14px", fontWeight: "800", margin: 0, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: "340px", color: "#ffffff" }} title={document?.title}>
            RAG Source Document Chunk Inspector
          </h2>
        </div>

        {/* Filters and Search Controls */}
        <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
          {/* Capsule Search Input */}
          <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
            <input
              type="text"
              placeholder="Search chunks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ 
                height: "34px", 
                fontSize: "11px", 
                width: "180px",
                background: "#16181d",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: "var(--radius-md)",
                padding: "0 10px 0 28px",
                color: "#ffffff",
                outline: "none"
              }}
            />
            <span style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", fontSize: "11px", opacity: 0.4 }}>🔍</span>
          </div>

          {/* Sort Switch Pills */}
          <div style={{ display: "flex", gap: "2px", background: "#16181d", border: "1px solid rgba(255,255,255,0.08)", borderRadius: "var(--radius-md)", padding: "2px" }}>
            <button 
              type="button"
              onClick={() => setSortBy("similarity")}
              style={{ 
                height: "26px", 
                fontSize: "11px", 
                padding: "0 12px", 
                borderRadius: "var(--radius-sm)",
                background: sortBy === "similarity" ? accentColor : "transparent",
                color: sortBy === "similarity" ? "black" : "rgba(255,255,255,0.6)",
                border: "none",
                fontWeight: "700",
                cursor: "pointer"
              }}
            >
              Similarity
            </button>
            <button 
              type="button"
              onClick={() => setSortBy("length")}
              style={{ 
                height: "26px", 
                fontSize: "11px", 
                padding: "0 12px", 
                borderRadius: "var(--radius-sm)",
                background: sortBy === "length" ? accentColor : "transparent",
                color: sortBy === "length" ? "black" : "rgba(255,255,255,0.6)",
                border: "none",
                fontWeight: "700",
                cursor: "pointer"
              }}
            >
              Length
            </button>
          </div>

          {/* Re-chunk Button styled as dark theme button */}
          <button
            type="button"
            disabled={rechunking}
            onClick={handleRechunk}
            style={{ 
              height: "34px", 
              padding: "0 16px", 
              fontSize: "11px", 
              border: "1px solid rgba(255,255,255,0.12)", 
              borderRadius: "var(--radius-md)", 
              color: "rgba(255,255,255,0.8)",
              background: "#1e222b",
              cursor: "pointer",
              fontWeight: "600",
              transition: "background 0.2s"
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = "#282d39"}
            onMouseLeave={(e) => e.currentTarget.style.background = "#1e222b"}
          >
            {rechunking ? "Reindexing..." : "Re-chunk"}
          </button>

          {!inline && (
            <button 
              type="button"
              onClick={onClose}
              style={{ 
                padding: 0, 
                width: "32px", 
                height: "32px", 
                fontSize: "16px", 
                marginLeft: "12px", 
                borderRadius: "50%", 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center", 
                border: "1px solid rgba(255,255,255,0.12)", 
                color: "#ffffff",
                background: "#1e222b",
                cursor: "pointer"
              }} 
              onMouseEnter={(e) => e.currentTarget.style.background = "#282d39"}
              onMouseLeave={(e) => e.currentTarget.style.background = "#1e222b"}
              title="Close Panel"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div style={{ flex: 1, display: "grid", placeItems: "center" }}>
          <div className="spinner" />
        </div>
      ) : (
        /* Split View Columns */
        <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
          
          {/* Left Column: Code Editor Style Raw Document View */}
          <div 
            ref={containerRef}
            style={{ 
              width: "50%", 
              borderRight: "1px solid rgba(255,255,255,0.06)", 
              overflowY: "auto", 
              padding: "20px 0",
              background: "#08090a"
            }}
          >
            <h3 style={{ fontSize: "11px", fontWeight: "800", color: accentColor, textTransform: "uppercase", letterSpacing: "0.1em", padding: "0 24px 12px 24px", borderBottom: "1px solid rgba(255,255,255,0.06)", marginBottom: "16px" }}>
              RAW DOCUMENT VIEWER: {document?.title || "Source"}
            </h3>
            
            {/* Line by line display */}
            <div style={{ display: "flex", flexDirection: "column" }}>
              {documentLines.map((line, idx) => {
                const isHighlighted = idx >= activeLineRange.start && idx <= activeLineRange.end;
                return (
                  <div 
                    key={idx} 
                    id={`doc-line-${idx}`}
                    style={{ 
                      display: "flex", 
                      background: isHighlighted ? "rgba(0, 217, 146, 0.12)" : "transparent",
                      borderLeft: isHighlighted ? `3px solid ${accentColor}` : "3px solid transparent",
                      padding: "1.5px 0"
                    }}
                  >
                    <span 
                      style={{ 
                        width: "48px", 
                        textAlign: "right", 
                        paddingRight: "16px", 
                        color: "rgba(255,255,255,0.3)", 
                        userSelect: "none",
                        fontFamily: "var(--font-mono)",
                        fontSize: "11px",
                        opacity: isHighlighted ? 0.9 : 0.4
                      }}
                    >
                      {idx + 1}
                    </span>
                    <span 
                      style={{ 
                        flex: 1, 
                        whiteSpace: "pre-wrap", 
                        color: isHighlighted ? accentColor : "rgba(255,255,255,0.75)",
                        fontFamily: "var(--font-mono)",
                        fontSize: "12px",
                        lineHeight: "1.6"
                      }}
                    >
                      {line || " "}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Dynamic Vertical Stack of Chunk Cards matching V2 Mockup */}
          <div 
            style={{ 
              width: "50%", 
              padding: "24px",
              display: "flex",
              flexDirection: "column",
              gap: "16px",
              overflowY: "auto",
              background: "#0f1114"
            }}
          >
            <h3 style={{ fontSize: "11px", fontWeight: "800", color: "#ffffff", textTransform: "uppercase", letterSpacing: "0.1em", borderBottom: "1px solid rgba(255,255,255,0.06)", paddingBottom: "12px", margin: 0 }}>
              DOCUMENT CHUNKS ({filteredChunks.length} Total)
            </h3>

            {filteredChunks.length === 0 ? (
              <p style={{ fontSize: "13px", color: "rgba(255,255,255,0.4)", fontStyle: "italic", padding: "12px" }}>
                No chunks matched the filter.
              </p>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {filteredChunks.map((chunk, idx) => {
                  const isSelected = selectedChunkIndex === idx;
                  const txt = chunk.content || chunk.text || "";
                  
                  return (
                    <div
                      key={chunk.id || idx}
                      onClick={() => setSelectedChunkIndex(idx)}
                      style={{
                        padding: "16px",
                        borderRadius: "var(--radius-lg)",
                        border: isSelected ? `1.5px solid ${accentColor}` : "1px solid rgba(255,255,255,0.06)",
                        background: isSelected ? "rgba(0, 217, 146, 0.02)" : "rgba(255,255,255,0.01)",
                        cursor: "pointer",
                        transition: "all var(--motion-fast) var(--ease-standard)",
                        boxShadow: isSelected ? `0 0 16px rgba(0, 217, 146, 0.12)` : "none"
                      }}
                    >
                      <div style={{ fontWeight: "700", fontSize: "12.5px", color: "#ffffff", display: "flex", justifyContent: "space-between" }}>
                        <span style={{ color: isSelected ? accentColor : "#ffffff" }}>
                          Chunk #{idx + 1} {isSelected && "(Selected)"}
                        </span>
                        <span style={{ fontSize: "10.5px", color: "rgba(255,255,255,0.3)" }}>•••</span>
                      </div>

                      <p style={{ 
                        fontSize: "12.5px", 
                        color: "rgba(255,255,255,0.7)", 
                        lineHeight: "1.55", 
                        margin: "8px 0 12px 0",
                        whiteSpace: isSelected ? "normal" : "nowrap",
                        overflow: isSelected ? "visible" : "hidden",
                        textOverflow: isSelected ? "clip" : "ellipsis",
                        fontFamily: "inherit"
                      }}>
                        "{txt.slice(0, 260)}{txt.length > 260 && "..."}"
                      </p>

                      <div style={{ display: "flex", flexWrap: "wrap", gap: "16px", fontSize: "11px", color: "rgba(255,255,255,0.45)", borderTop: isSelected ? "1px solid rgba(255,255,255,0.06)" : "none", paddingTop: isSelected ? "10px" : "0" }}>
                        <div>
                          <span>Cosine Similarity:</span>{" "}
                          <span style={{ fontWeight: "800", color: isSelected ? accentColor : "rgba(255,255,255,0.7)" }}>
                            {getMockSimilarity(txt)}
                          </span>
                        </div>
                        <div>
                          <span>Tokens Count:</span>{" "}
                          <span style={{ fontWeight: "800", color: "rgba(255,255,255,0.7)" }}>
                            {Math.round(txt.length / 4.2)}
                          </span>
                        </div>
                        {isSelected && (
                          <>
                            <div>
                              <span>Character Count:</span>{" "}
                              <span style={{ fontWeight: "800", color: "rgba(255,255,255,0.7)" }}>
                                {txt.length}
                              </span>
                            </div>
                            <div>
                              <span>Model:</span>{" "}
                              <span style={{ fontWeight: "800", color: "rgba(255,255,255,0.7)" }}>
                                text-embedding-3-small
                              </span>
                            </div>
                          </>
                        )}
                      </div>

                      {/* Integrated Note Editor inside selected card */}
                      {isSelected && (
                        <NoteEditor chunkId={chunk.id} />
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

        </div>
      )}
    </div>
  );

  if (inline) {
    return contentElement;
  }

  return createPortal(
    <div 
      className="modal-overlay" 
      onClick={onClose}
      style={{ 
        position: "fixed", 
        inset: 0, 
        background: "rgba(0,0,0,0.75)", 
        backdropFilter: "blur(6px)",
        WebkitBackdropFilter: "blur(6px)",
        zIndex: 999, 
        display: "grid", 
        placeItems: "center"
      }}
    >
      <div onClick={e => e.stopPropagation()}>
        {contentElement}
      </div>
    </div>,
    window.document.body
  );
}
