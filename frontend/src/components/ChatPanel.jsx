import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  createChatSession,
  listChatSessions,
  getChatSession,
  getChatHistory,
  streamChatTurn,
  cancelChatTurn,
  deleteChatSession,
} from "../api/chat";
import { generateProduct, listCollections, listDocuments } from "../api/knowledgeApi";
import { useWorkspace } from "../context/WorkspaceContext";
import XRayPanel from "./XRayPanel";
import CitationModal from "./CitationModal";
import CitationBadge from "./CitationBadge";

const PRODUCT_TYPES = [
  { key: "study-guide", label: "Study Guide", emoji: "📘" },
  { key: "briefing-doc", label: "Briefing Doc", emoji: "📋" },
  { key: "faq", label: "FAQ", emoji: "❓" },
  { key: "timeline", label: "Timeline", emoji: "📅" },
  { key: "glossary", label: "Glossary", emoji: "📖" },
  { key: "flashcards", label: "Flashcards", emoji: "🃏" },
];

function FlashcardBlock({ card }) {
  const [revealed, setRevealed] = useState(false);
  return (
    <div className="flashcard" onClick={() => setRevealed(!revealed)} style={{ margin: "4px 0", padding: "10px 14px" }}>
      <div className="flashcard-question">{card.question}</div>
      {revealed && <div className="flashcard-answer">{card.answer}</div>}
    </div>
  );
}

function parseInline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

function MarkdownBlock({ content }) {
  const lines = content.split("\n");
  return (
    <div className="markdown-body">
      {lines.map((line, i) => {
        if (line.startsWith("```")) return null;
        if (line.startsWith("# ")) return <h1 key={i}>{parseInline(line.slice(2))}</h1>;
        if (line.startsWith("## ")) return <h2 key={i}>{parseInline(line.slice(3))}</h2>;
        if (line.startsWith("### ")) return <h3 key={i}>{parseInline(line.slice(4))}</h3>;
        if (line.startsWith("- ")) return <li key={i} style={{ fontSize: "13px", margin: "2px 0" }}>{parseInline(line.slice(2))}</li>;
        if (line.trim() === "") return <br key={i} />;
        return <p key={i} style={{ fontSize: "13px", margin: "4px 0", lineHeight: "1.5" }}>{parseInline(line)}</p>;
      })}
    </div>
  );
}


export default function ChatPanel() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { selectedCollectionId, selectedDocumentIds, collectionName, addGeneratedProduct, selectCollection, setActiveChunkId } = useWorkspace();

  const [sessions, setChatSessions] = useState([]);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [activeTurnId, setActiveTurnId] = useState(null);
  const generateMenuRef = useRef(null);
  const messagesEndRef = useRef(null);

  const [debugMode, setDebugMode] = useState(false);
  const [debugTrace, setDebugTrace] = useState(null);
  const [activeCitation, setActiveCitation] = useState(null);
  const [activeChunk, setActiveChunk] = useState(null);
  const [showSessionList, setShowSessionList] = useState(false);
  const [showGenerateMenu, setShowGenerateMenu] = useState(false);

  const hasScope = !!selectedCollectionId;

  useEffect(() => {
    if (selectedCollectionId) {
      listChatSessions(selectedCollectionId).then(setChatSessions).catch(console.error);
    } else {
      setChatSessions([]);
    }
  }, [selectedCollectionId]);

  useEffect(() => {
    if (sessionId) {
      getChatSession(sessionId)
        .then(async (session) => {
          if (!session.collection_id) return;
          
          if (!selectedCollectionId) {
            // Direct URL load: resolve and select collection
            try {
              const cols = await listCollections();
              const col = cols.find((c) => c.id === session.collection_id);
              const docs = await listDocuments({ collectionId: session.collection_id });
              selectCollection(session.collection_id, col?.name || "Untitled", docs);
            } catch (err) {
              console.error("Failed to auto-select collection:", err);
            }
          } else if (selectedCollectionId !== session.collection_id) {
            // Collection mismatch (user switched collection): close session and go back to /chat
            navigate("/chat");
          }
        })
        .catch(console.error);
    }
  }, [sessionId, selectedCollectionId, selectCollection, navigate]);

  useEffect(() => {
    if (sessionId) {
      getChatHistory(sessionId)
        .then((history) => {
          if (isGenerating && history.length === 0) return;
          const formatted = [];
          history.forEach((turn) => {
            formatted.push({ role: "user", content: turn.query_text });
            if (turn.answer_text) {
              formatted.push({
                role: "assistant",
                content: turn.answer_text,
                citations: turn.citations
                  ? turn.citations.map((c) => ({
                      ...c,
                      metadata: c.metadata_json ? JSON.parse(c.metadata_json) : null,
                    }))
                  : [],
                chunks: turn.retrieved_chunks_json
                  ? JSON.parse(turn.retrieved_chunks_json)
                  : [],
                conflict_status: turn.conflict_status || "no_conflict",
                conflict_details: turn.conflict_details,
                trace: {
                  retrieval: turn.retrieval_trace,
                  safety: turn.safety_trace,
                  evaluation: turn.evaluation_metrics,
                },
              });
            }
          });
          setMessages(formatted);
        })
        .catch(console.error);
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, statusMessage]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isGenerating || !hasScope) return;

    let sid = sessionId;
    let isNew = false;

    if (!sid) {
      try {
        const session = await createChatSession(selectedCollectionId);
        setChatSessions([session, ...sessions]);
        sid = session.id;
        isNew = true;
        navigate(`/chat/${sid}`);
      } catch (err) {
        alert("Failed to create session");
        return;
      }
    }

    _submitMessage(sid, inputValue, isNew);
    setInputValue("");
  };

  const _submitMessage = (sid, text, clear = false) => {
    if (clear) {
      setMessages([{ role: "user", content: text }]);
    } else {
      setMessages((prev) => [...prev, { role: "user", content: text }]);
    }

    setIsGenerating(true);
    setStatusMessage("Starting...");
    setMessages((prev) => [...prev, { role: "assistant", content: "", isStreaming: true }]);

    streamChatTurn(sid, text, {
      onStatus: (data) => {
        setStatusMessage(data.message);
        if (data.turn_id) setActiveTurnId(data.turn_id);
      },
      onToken: (token) => {
        setMessages((prev) => {
          if (prev.length === 0) return prev;
          const last = prev[prev.length - 1];
          if (last.role !== "assistant") return prev;
          return [...prev.slice(0, -1), { ...last, content: last.content + token }];
        });
      },
      onCitations: (data) => {
        setMessages((prev) => {
          if (prev.length === 0) return prev;
          const last = prev[prev.length - 1];
          if (last.role !== "assistant") return prev;
          return [
            ...prev.slice(0, -1),
            {
              ...last,
              citations: data.citations,
              chunks: data.retrieved_chunks,
              conflict_status: data.conflict_status || "no_conflict",
              conflict_details: data.conflict_details,
            },
          ];
        });
      },
      onTrace: (trace) => {
        setMessages((prev) => {
          if (prev.length === 0) return prev;
          const last = prev[prev.length - 1];
          if (last.role !== "assistant") return prev;
          return [...prev.slice(0, -1), { ...last, trace }];
        });
        setDebugTrace(trace);
      },
      onError: (err) => {
        setStatusMessage(`Error: ${err.message}`);
        setIsGenerating(false);
      },
      onDone: () => {
        setMessages((prev) => {
          if (prev.length === 0) return prev;
          const last = prev[prev.length - 1];
          if (last.role !== "assistant") return prev;
          return [...prev.slice(0, -1), { ...last, isStreaming: false }];
        });
        setIsGenerating(false);
        setStatusMessage("");
        setActiveTurnId(null);
      },
    });
  };

  const handleCancel = async () => {
    if (activeTurnId) {
      await cancelChatTurn(activeTurnId);
      setStatusMessage("Cancellation requested...");
    }
  };

  const handleDeleteSession = async (e, sid) => {
    e.stopPropagation();
    if (isGenerating && sid === sessionId) {
      alert("Cannot delete an active session while it is generating.");
      return;
    }
    if (!window.confirm("Are you sure you want to delete this chat session?")) return;
    try {
      await deleteChatSession(sid);
      setChatSessions((prev) => prev.filter((s) => s.id !== sid));
      if (sid === sessionId) {
        navigate("/chat");
        setMessages([]);
      }
    } catch (err) {
      alert("Failed to delete session");
    }
  };

  useEffect(() => {
    if (!showGenerateMenu) return;
    function handleClick(e) {
      if (generateMenuRef.current && !generateMenuRef.current.contains(e.target)) {
        setShowGenerateMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [showGenerateMenu]);

  const handleCitationClick = (citation, chunks) => {
    const chunk = chunks.find((c) => c.chunk_id === citation.chunk_id);
    if (chunk) {
      setActiveCitation(citation);
      setActiveChunk(chunk);
    }
  };

  const handleInlineGenerate = async (productType) => {
    setShowGenerateMenu(false);
    if (!hasScope || isGenerating) return;

    const pt = PRODUCT_TYPES.find((p) => p.key === productType);
    const tempId = `gen-${Date.now()}`;

    setMessages((prev) => [
      ...prev,
      {
        id: tempId,
        role: "assistant",
        content: "",
        isGenerating: true,
        isGenerated: true,
        productType,
        productLabel: pt.label,
      },
    ]);

    try {
      const result = await generateProduct(selectedCollectionId, productType);
      const content = result.content || result;

      const product = {
        id: `${productType}-${Date.now()}`,
        type: productType,
        label: pt.label,
        content,
        createdAt: new Date().toISOString(),
      };
      addGeneratedProduct(product);

      setMessages((prev) =>
        prev.map((m) =>
          m.id === tempId
            ? { ...m, content, isGenerating: false }
            : m
        )
      );
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === tempId
            ? { ...m, content: `Error: ${err.message}`, isGenerating: false }
            : m
        )
      );
    }
  };

  const renderMessageContent = (msg) => {
    if (msg.isGenerated) {
      if (msg.isGenerating) {
        return <span className="status-badge" style={{ background: "var(--ai-thinking)", color: "var(--accent-strong)", border: "none", height: "auto", padding: "6px 12px" }}>Generating {msg.productLabel}...</span>;
      }
      if (msg.productType === "flashcards") {
        const cards = Array.isArray(msg.content) ? msg.content : [];
        return (
          <div>
            <div style={{ fontSize: "14px", fontWeight: 600, marginBottom: "8px" }}>🃏 {msg.productLabel}</div>
            {cards.map((card, i) => <FlashcardBlock key={i} card={card} />)}
          </div>
        );
      }
      const text = typeof msg.content === "string" ? msg.content : "";
      return (
        <div>
          <div style={{ fontSize: "14px", fontWeight: 600, marginBottom: "8px" }}>{msg.productLabel}</div>
          <MarkdownBlock content={text} />
        </div>
      );
    }
    if (msg.role !== "assistant" || !msg.citations || msg.citations.length === 0) {
      return msg.content;
    }
    const parts = msg.content.split(/(\[Source\s+[^\]]+\]|\[\d+\])/g);
    return parts.map((part, idx) => {
      const match = part.match(/\[Source\s+([^\]]+)\]|\[(\d+)\]/);
      if (match) {
        const label = (match[1] || match[2]).trim();
        let targetCit = null;
        if (/^\d+$/.test(label)) {
          const index = parseInt(label, 10) - 1;
          targetCit = msg.citations?.[index];
        }
        if (!targetCit && msg.citations) {
          targetCit = msg.citations.find((c) => c.chunk_id === label);
        }
        let targetChunk = null;
        if (targetCit) {
          targetChunk = (msg.chunks || []).find((c) => c.chunk_id === targetCit.chunk_id);
        }
        let docTitle = "";
        if (targetChunk) {
          docTitle = targetChunk.title || targetChunk.metadata?.title || "";
        }
        if (!docTitle && targetCit) {
          docTitle = targetCit.title || targetCit.metadata?.title || "";
        }
        const displayLabel = docTitle ? `Source ${label} - ${docTitle}` : `Source ${label}`;
        return (
          <CitationBadge
            key={idx}
            label={displayLabel}
            citation={targetCit}
            chunk={targetChunk}
            onClick={() => {
              if (targetCit) handleCitationClick(targetCit, msg.chunks || []);
            }}
          />
        );
      }
      return part;
    });
  };

  const accentColor = "var(--kb-accent)";

  if (!hasScope) {
    return (
      <div className="chat-panel-empty" style={{ background: "var(--surface)", height: "100%" }}>
        <div className="panel-empty-state">
          <span style={{ fontSize: "32px", marginBottom: "12px" }}>💬</span>
          <h3 style={{ margin: "0 0 8px", fontSize: "16px", color: "var(--text-primary)" }}>Select a collection folder</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "14px", margin: 0 }}>
            Choose a workspace folder from the Documents panel to start chatting.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-panel" style={{ height: "100%", display: "flex", flexDirection: "column", background: "var(--surface)" }}>
      {/* 1. Header Area matching mockup */}
      <div className="chat-panel-header" style={{ padding: "16px 20px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border)" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "2px", alignItems: "flex-start" }}>
          <span style={{ fontSize: "14.5px", fontWeight: "800", color: "var(--text-primary)" }}>
            Chat: {collectionName || "Market Analysis Q3 2023"}
          </span>
          <span 
            onClick={() => selectCollection(null, null, [])}
            style={{ 
              fontSize: "11px", 
              color: accentColor, 
              cursor: "pointer", 
              textDecoration: "underline",
              fontWeight: "600"
            }}
          >
            📂 {selectedDocumentIds.length > 0 ? selectedDocumentIds.length : "25"} sources
          </span>
        </div>
        
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <button
            onClick={() => setShowSessionList(!showSessionList)}
            className={`button ${showSessionList ? "button-primary" : "button-ghost"}`}
            style={{ fontSize: "11px", height: "30px", padding: "0 10px", borderRadius: "var(--radius-sm)" }}
          >
            Sessions
          </button>
          
          {/* Settings wheel redirect */}
          <button
            onClick={() => navigate("/settings")}
            className="button button-ghost"
            style={{ 
              fontSize: "11px", 
              height: "30px", 
              padding: "0 10px", 
              borderRadius: "var(--radius-sm)",
              display: "flex",
              alignItems: "center",
              gap: "4px",
              border: "1px solid var(--border)"
            }}
            title="Configure RAG Parameters"
          >
            ⚙️ RAG Settings
          </button>
        </div>
      </div>

      {showSessionList && (
        <div className="chat-panel-sessions" style={{ background: "rgba(0, 0, 0, 0.05)", borderBottom: "1px solid var(--border)" }}>
          {sessions.map((s) => (
            <div
              key={s.id}
              onClick={() => navigate(`/chat/${s.id}`)}
              className={`session-item ${sessionId === s.id ? "session-item-active" : ""}`}
              style={{ margin: "2px 0", padding: "8px 12px" }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="mono" style={{ fontSize: "11px", opacity: 0.6 }}>
                  {s.id.slice(0, 8)}
                </div>
                <div style={{ fontSize: "12px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                  {new Date(s.created_at).toLocaleDateString()}
                </div>
              </div>
              <button
                onClick={(e) => handleDeleteSession(e, s.id)}
                className="delete-button"
                title="Delete Session"
                disabled={isGenerating && s.id === sessionId}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      {/* 2. Messages List Area */}
      <div className="messages-list" style={{ flex: 1, overflowY: "auto", padding: "24px", display: "flex", flexDirection: "column", gap: "24px" }}>
        {messages.length === 0 && !isGenerating && (
          <div style={{ textAlign: "center", marginTop: "80px", padding: "0 40px" }}>
            <h2 style={{ fontSize: "20px", fontWeight: "750", marginBottom: "8px" }}>Ask about your documents</h2>
            <p style={{ color: "var(--text-secondary)", fontSize: "14px", margin: 0 }}>
              {collectionName
                ? `Ask anything about the ${selectedDocumentIds.length} selected documents.`
                : "Select a folder from the Documents panel."}
            </p>
          </div>
        )}
        
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              gap: "12px",
              alignSelf: msg.role === "user" ? "flex-end" : "flex-start",
              maxWidth: msg.role === "user" ? "85%" : "100%",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              width: msg.role === "user" ? "auto" : "100%"
            }}
          >
            {/* AI Avatar */}
            {msg.role !== "user" && (
              <div style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                background: "rgba(0, 217, 146, 0.08)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: accentColor,
                fontSize: "14px",
                fontWeight: "800",
                flexShrink: 0,
                border: `1.5px solid ${accentColor}`,
                boxShadow: `0 0 10px rgba(0, 217, 146, 0.15)`
              }}>
                KB
              </div>
            )}

            {/* Bubble Panel */}
            <div
              className={`message-bubble ${msg.role === "user" ? "message-user" : "message-assistant"}`}
              style={{
                margin: 0,
                flex: msg.role === "user" ? "none" : 1,
                background: msg.role === "user" ? "var(--surface-raised)" : "var(--surface-muted)",
                border: "1px solid var(--border)",
                borderRadius: msg.role === "user" 
                  ? "var(--radius-lg) var(--radius-lg) 0 var(--radius-lg)" 
                  : "var(--radius-lg) var(--radius-lg) var(--radius-lg) 0",
                padding: "14px 20px",
                color: "var(--text-primary)",
                boxShadow: "var(--shadow-xs)"
              }}
            >
              {/* Header Label inside Bubble */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px", borderBottom: "1px solid var(--border)", paddingBottom: "6px" }}>
                <span style={{ fontSize: "11px", fontWeight: "750", color: msg.role === "user" ? "var(--text-primary)" : accentColor }}>
                  {msg.role === "user" ? "User" : "KnowledgeBaseLab"}
                </span>
                <span style={{ fontSize: "10px", color: "var(--text-muted)" }}>
                  {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>

              {/* Message content */}
              <div style={{ fontSize: "13px", lineHeight: "1.6" }}>
                {renderMessageContent(msg)}
              </div>

              {/* Cited References bottom list */}
              {msg.role !== "user" && msg.citations && msg.citations.length > 0 && (
                <div style={{ borderTop: "1px solid var(--border)", marginTop: "16px", paddingTop: "12px" }}>
                  <span style={{ fontSize: "10px", fontWeight: "800", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: "6px" }}>
                    Cited References:
                  </span>
                  <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                    {msg.citations.map((cit, cidx) => {
                      const matchingChunk = (msg.chunks || []).find(c => c.chunk_id === cit.chunk_id);
                      const title = cit.title || matchingChunk?.title || cit.metadata?.title || "Document Source";
                      return (
                        <div 
                          key={cidx} 
                          style={{ 
                            fontSize: "11px", 
                            color: "var(--text-secondary)", 
                            cursor: "pointer", 
                            display: "flex", 
                            alignItems: "center", 
                            gap: "6px" 
                          }}
                          onClick={() => handleCitationClick(cit, msg.chunks || [])}
                          className="ref-item-hover"
                        >
                          <span style={{ color: accentColor, fontWeight: "750" }}>[{cidx + 1}]</span>
                          <span style={{ textDecoration: "underline" }}>{title}</span>
                          {cit.page_number && <span style={{ opacity: 0.6 }}>(p. {cit.page_number})</span>}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {msg.conflict_status === "unresolved_conflict" && (
                <div
                  style={{
                    marginTop: "12px",
                    padding: "10px 14px",
                    backgroundColor: "rgba(239, 68, 68, 0.08)",
                    borderLeft: "4px solid #ef4444",
                    borderRadius: "var(--radius-md)",
                    fontSize: "13px",
                    color: "#ef4444",
                  }}
                >
                  <div style={{ fontWeight: "600" }}>⚠️ Warning: Source Contradiction Detected</div>
                  <div style={{ marginTop: "4px" }}>
                    Sources in this collection contain conflicting claims on this topic.
                  </div>
                  {msg.conflict_details && (
                    <div style={{ fontSize: "11px", opacity: 0.85, marginTop: "4px" }}>
                      <strong>Details:</strong> {msg.conflict_details}
                    </div>
                  )}
                </div>
              )}
              
              {debugMode && msg.trace && (
                <div style={{ marginTop: "12px" }}>
                  <button
                    onClick={() => setDebugTrace(msg.trace)}
                    className="button button-ghost"
                    style={{ fontSize: "11px", height: "24px", padding: "0 8px", background: "var(--surface)" }}
                  >
                    🔍 Pipeline X-Ray
                  </button>
                </div>
              )}
            </div>

            {/* User Avatar */}
            {msg.role === "user" && (
              <div style={{
                width: "36px",
                height: "36px",
                borderRadius: "50%",
                background: "var(--accent-soft)",
                border: "1.5px solid var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "var(--accent-strong)",
                fontSize: "13px",
                fontWeight: "750",
                flexShrink: 0,
                boxShadow: "var(--shadow-xs)"
              }}>
                U
              </div>
            )}
          </div>
        ))}
        
        {statusMessage && (
          <div
            className="status-badge"
            style={{ alignSelf: "flex-start", height: "28px", background: "var(--ai-thinking)", color: accentColor, border: "none" }}
          >
            {statusMessage}...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 3. Composer capsule form input */}
      <form 
        onSubmit={handleSendMessage} 
        style={{ 
          borderTop: "1px solid var(--border)", 
          background: "transparent", 
          padding: "16px 20px" 
        }}
      >
        <div 
          style={{ 
            display: "flex", 
            alignItems: "center", 
            gap: "12px", 
            padding: "6px 14px",
            background: "var(--surface-muted)",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-lg)"
          }}
        >
          {/* Left accessories: attachment & mic */}
          <div style={{ display: "flex", gap: "8px", color: "var(--text-muted)", fontSize: "16px", cursor: "pointer" }}>
            <span title="Attach file" onClick={() => alert("Upload source directly in sidebar panel.")}>📎</span>
            <span title="Voice prompt (Mocked)">🎙️</span>
          </div>

          {/* Central Input Box */}
          <input
            type="text"
            className="composer-input"
            placeholder={`Ask anything about your data... | Context: ${collectionName || "All Sources"}`}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isGenerating || !hasScope}
            style={{ 
              background: "transparent", 
              border: "none", 
              flex: 1, 
              padding: "8px 0",
              color: "var(--text-primary)",
              fontSize: "13px",
              outline: "none"
            }}
          />

          {hasScope && (
            <div className="composer-generate" ref={generateMenuRef} style={{ position: "relative" }}>
              <button
                type="button"
                onClick={() => setShowGenerateMenu(!showGenerateMenu)}
                className="button button-ghost"
                disabled={isGenerating}
                style={{ fontSize: "11px", height: "28px", padding: "0 10px", border: "1px solid var(--border)", borderRadius: "var(--radius-sm)" }}
              >
                + Generate
              </button>
              {showGenerateMenu && (
                <div className="generate-dropdown" style={{ position: "absolute", bottom: "36px", right: 0, zIndex: 10 }}>
                  {PRODUCT_TYPES.map((pt) => (
                    <button
                      key={pt.key}
                      type="button"
                      onClick={() => handleInlineGenerate(pt.key)}
                      className="generate-dropdown-item"
                    >
                      <span>{pt.emoji}</span>
                      <span>{pt.label}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Right send button styled in electric green */}
          {isGenerating ? (
            <button 
              type="button" 
              onClick={handleCancel} 
              className="button button-ghost" 
              style={{ color: "var(--danger)", height: "30px", fontSize: "11px" }}
            >
              Cancel
            </button>
          ) : (
            <button 
              type="submit" 
              disabled={!inputValue.trim()}
              style={{ 
                width: "28px", 
                height: "28px", 
                padding: 0, 
                borderRadius: "50%", 
                display: "flex", 
                alignItems: "center", 
                justifyContent: "center", 
                minWidth: "28px",
                background: accentColor,
                color: "black",
                fontWeight: "800",
                border: "none",
                cursor: "pointer",
                opacity: inputValue.trim() ? 1 : 0.4
              }}
              title="Send Message"
            >
              ➔
            </button>
          )}
        </div>
      </form>

      <XRayPanel trace={debugTrace} onClose={() => setDebugTrace(null)} />
      <CitationModal
        citation={activeCitation}
        chunk={activeChunk}
        onClose={() => { setActiveCitation(null); setActiveChunk(null); }}
      />
    </div>
  );
}
