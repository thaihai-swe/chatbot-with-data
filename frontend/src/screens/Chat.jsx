import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  createChatSession, 
  listChatSessions, 
  getChatHistory, 
  streamChatTurn,
  cancelChatTurn,
  deleteChatSession
} from "../api/chat";
import { listCollections } from "../api/knowledgeApi";
import XRayPanel from "../components/XRayPanel";
import CitationModal from "../components/CitationModal";

export default function ChatScreen() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [sessions, setChatSessions] = useState([]);
  const [availableCollections, setAvailableCollections] = useState([]);
  const [selectedCollections, setSelectedCollections] = useState([]);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [activeTurnId, setActiveTurnId] = useState(null);
  const messagesEndRef = useRef(null);

  const [showSettings, setShowSettings] = useState(false);
  const [debugMode, setDebugMode] = useState(false);
  const [debugTrace, setDebugTrace] = useState(null);
  const [activeCitation, setActiveCitation] = useState(null);
  const [activeChunk, setActiveChunk] = useState(null);

  // Load sessions
  useEffect(() => {
    listChatSessions().then(setChatSessions).catch(console.error);
    listCollections().then(setAvailableCollections).catch(console.error);
  }, []);

  // Load history when sessionId changes
  useEffect(() => {
    if (sessionId) {
      // Find session in list to get its collections
      const currentSession = sessions.find(s => s.id === sessionId);
      if (currentSession) {
        setSelectedCollections(currentSession.collection_ids || []);
      }

      getChatHistory(sessionId)
        .then(history => {
          // If we are currently generating and history is empty, it's a new session
          // we just initialized locally. Don't let the empty history wipe it.
          if (isGenerating && history.length === 0) return;

          const formatted = [];
          history.forEach(turn => {
            formatted.push({ role: "user", content: turn.query_text });
            if (turn.answer_text) {
              formatted.push({ 
                role: "assistant", 
                content: turn.answer_text,
                citations: turn.citations ? turn.citations.map(c => ({
                  ...c,
                  metadata: c.metadata_json ? JSON.parse(c.metadata_json) : null
                })) : [],
                chunks: turn.retrieved_chunks_json ? JSON.parse(turn.retrieved_chunks_json) : [],
                conflict_status: turn.conflict_status || "no_conflict",
                conflict_details: turn.conflict_details,
                trace: {
                  retrieval: turn.retrieval_trace,
                  safety: turn.safety_trace,
                  evaluation: turn.evaluation_metrics
                }
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

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, statusMessage]);

  const handleCreateSession = async () => {
    try {
      const session = await createChatSession(selectedCollections);
      setChatSessions([session, ...sessions]);
      navigate(`/chat/${session.id}`);
    } catch (err) {
      alert("Failed to create session");
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isGenerating) return;

    let sid = sessionId;
    let isNew = false;

    if (!sid) {
      try {
        const session = await createChatSession(selectedCollections);
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
      setMessages(prev => [...prev, { role: "user", content: text }]);
    }
    
    setIsGenerating(true);
    setStatusMessage("Starting...");
    
    // Add placeholder for assistant
    setMessages(prev => [...prev, { role: "assistant", content: "", isStreaming: true }]);

    const cleanup = streamChatTurn(sid, text, {
      onStatus: (data) => {
        setStatusMessage(data.message);
        if (data.turn_id) setActiveTurnId(data.turn_id);
      },
      onToken: (token) => {
        setMessages(prev => {
          if (prev.length === 0) return prev;
          const last = prev[prev.length - 1];
          if (last.role !== "assistant") return prev;
          return [...prev.slice(0, -1), { ...last, content: last.content + token }];
        });
      },
      onCitations: (data) => {
        setMessages(prev => {
          if (prev.length === 0) return prev;
          const last = prev[prev.length - 1];
          if (last.role !== "assistant") return prev;
          return [...prev.slice(0, -1), { 
            ...last, 
            citations: data.citations, 
            chunks: data.retrieved_chunks,
            conflict_status: data.conflict_status || "no_conflict",
            conflict_details: data.conflict_details
          }];
        });
      },
      onTrace: (trace) => {
        setMessages(prev => {
          if (prev.length === 0) return prev;
          const last = prev[prev.length - 1];
          if (last.role !== "assistant") return prev;
          return [...prev.slice(0, -1), { ...last, trace: trace }];
        });
        setDebugTrace(trace);
      },
      onError: (err) => {
        setStatusMessage(`Error: ${err.message}`);
        setIsGenerating(false);
      },
      onDone: () => {
        setMessages(prev => {
          if (prev.length === 0) return prev;
          const last = prev[prev.length - 1];
          if (last.role !== "assistant") return prev;
          return [...prev.slice(0, -1), { ...last, isStreaming: false }];
        });
        setIsGenerating(false);
        setStatusMessage("");
        setActiveTurnId(null);
      }
    });
  };

  const handleCancel = async () => {
    if (activeTurnId) {
      await cancelChatTurn(activeTurnId);
      setStatusMessage("Cancellation requested...");
    }
  };

  const handleToggleCollection = (cid) => {
    setSelectedCollections(prev => 
      prev.includes(cid) ? prev.filter(id => id !== cid) : [...prev, cid]
    );
  };

  const handleDeleteSession = async (e, sid) => {
    e.stopPropagation();
    if (isGenerating && sid === sessionId) {
      alert("Cannot delete an active session while it is generating.");
      return;
    }

    if (!window.confirm("Are you sure you want to delete this chat session? This action cannot be undone.")) {
      return;
    }

    try {
      await deleteChatSession(sid);
      setChatSessions(prev => prev.filter(s => s.id !== sid));
      
      if (sid === sessionId) {
        navigate("/chat");
        setMessages([]);
      }
    } catch (err) {
      alert("Failed to delete session");
    }
  };

  const handleCitationClick = (citation, chunks) => {
    const chunk = chunks.find(c => c.chunk_id === citation.chunk_id);
    if (chunk) {
      setActiveCitation(citation);
      setActiveChunk(chunk);
    }
  };

  const renderMessageContent = (msg) => {
    if (msg.role !== "assistant" || !msg.citations || msg.citations.length === 0) {
      return msg.content;
    }

    const parts = msg.content.split(/(\[Source\s+[^\]]+\])/g);
    return parts.map((part, idx) => {
      const match = part.match(/\[Source\s+([^\]]+)\]/);
      if (match) {
        const label = match[1].trim();
        let title = "";
        
        if (/^\d+$/.test(label)) {
          const index = parseInt(label, 10) - 1;
          if (msg.chunks && msg.chunks[index]) {
            title = msg.chunks[index].title || msg.chunks[index].metadata?.title;
          } else if (msg.citations && msg.citations[index]) {
            title = msg.citations[index].metadata?.title || msg.citations[index].title;
          }
        }
        
        if (!title && msg.citations) {
          const cit = msg.citations.find(c => c.chunk_id === label);
          if (cit) {
            title = cit.metadata?.title || cit.title;
          }
        }

        if (!title) {
          title = `Source ${label}`;
        }

        return (
          <span 
            key={idx} 
            className="inline-citation-tag" 
            style={{ 
              cursor: "pointer", 
              color: "var(--accent-strong)", 
              fontWeight: "600",
              textDecoration: "underline",
              backgroundColor: "rgba(99, 102, 241, 0.08)",
              border: "1px solid var(--border)",
              padding: "2px 6px",
              borderRadius: "var(--radius-sm)",
              fontSize: "12px",
              margin: "0 2px"
            }}
            onClick={() => {
              let targetCit = null;
              if (/^\d+$/.test(label)) {
                const index = parseInt(label, 10) - 1;
                targetCit = msg.citations?.[index];
              }
              if (!targetCit && msg.citations) {
                targetCit = msg.citations.find(c => c.chunk_id === label);
              }
              if (targetCit) {
                handleCitationClick(targetCit, msg.chunks || []);
              }
            }}
            title={title}
          >
            [{title}]
          </span>
        );
      }
      return part;
    });
  };

  return (
    <div className="chat-container">
      <aside className="chat-sidebar">
        <div style={{ padding: "16px" }}>
          <button onClick={handleCreateSession} className="button button-primary" style={{ width: "100%", marginBottom: "16px" }}>
            + New Chat
          </button>
          
          <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
            <button onClick={() => setShowSettings(!showSettings)} className="button button-ghost" style={{ flex: 1, fontSize: "12px" }}>
              {showSettings ? "Hide Settings" : "Settings"}
            </button>
            <button 
              onClick={() => setDebugMode(!debugMode)} 
              className={`button ${debugMode ? "button-primary" : "button-ghost"}`} 
              style={{ flex: 1, fontSize: "12px" }}
            >
              {debugMode ? "Debug: ON" : "Debug: OFF"}
            </button>
          </div>
          
          {showSettings && (
            <div className="surface-card" style={{ marginBottom: "16px", padding: "12px", borderRadius: "var(--radius-md)" }}>
              <h4 style={{ margin: "0 0 12px 0", fontSize: "12px", textTransform: "uppercase", color: "var(--text-muted)", paddingTop: "4px" }}>Scope</h4>
              <div style={{ maxHeight: "120px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "6px" }}>
                {availableCollections.length === 0 && <div style={{ opacity: 0.5, fontSize: "11px" }}>No collections</div>}
                {availableCollections.map(c => (
                  <label key={c.id} className="config-toggle">
                    <input 
                      type="checkbox" 
                      checked={selectedCollections.includes(c.id)} 
                      onChange={() => handleToggleCollection(c.id)} 
                    /> 
                    <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.name}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="session-list" style={{ flex: 1, overflowY: "auto" }}>
          {sessions.map(s => (
            <div key={s.id} 
                onClick={() => navigate(`/chat/${s.id}`)}
                className={`session-item ${sessionId === s.id ? "session-item-active" : ""}`}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="mono" style={{ fontSize: "11px", opacity: 0.6 }}>{s.id.slice(0, 8)}</div>
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
      </aside>

      <div className="chat-main">
        <div className="messages-list">
          {messages.length === 0 && !isGenerating && (
            <div style={{ textAlign: "center", marginTop: "120px", padding: "0 40px" }}>
              <h2 style={{ fontSize: "22px", fontWeight: "600", marginBottom: "12px" }}>Ready to chat?</h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "15px" }}>Select a session or start typing to begin a conversation with your document knowledge base.</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-bubble ${msg.role === "user" ? "message-user" : "message-assistant"}`}>
              {renderMessageContent(msg)}
              {msg.conflict_status === "unresolved_conflict" && (
                <div style={{
                  marginTop: "12px",
                  padding: "10px 14px",
                  backgroundColor: "rgba(239, 68, 68, 0.08)",
                  borderLeft: "4px solid #ef4444",
                  borderRadius: "var(--radius-md)",
                  fontSize: "13px",
                  color: "#ef4444",
                  display: "flex",
                  flexDirection: "column",
                  gap: "4px"
                }}>
                  <div style={{ fontWeight: "600" }}>⚠️ Warning: Source Contradiction Detected</div>
                  <div>Sources in this collection contain conflicting claims on this topic that were not addressed in the response.</div>
                  {msg.conflict_details && (
                    <div style={{ fontSize: "11px", opacity: 0.85, marginTop: "2px" }}>
                      <strong>Details:</strong> {msg.conflict_details}
                    </div>
                  )}
                </div>
              )}
              {debugMode && msg.trace && (
                <div style={{ marginTop: "12px" }}>
                  <button onClick={() => setDebugTrace(msg.trace)} className="button button-ghost" style={{ fontSize: "11px", height: "24px", padding: "0 8px", background: "var(--surface)" }}>
                    🔍 Pipeline X-Ray
                  </button>
                </div>
              )}

            </div>
          ))}
          {statusMessage && (
            <div className="status-badge" style={{ alignSelf: "flex-start", height: "28px", background: "var(--ai-thinking)", color: "var(--accent-strong)", border: "none" }}>
              {statusMessage}...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="chat-input-form">
          <div className="composer-container">
            <input 
              type="text" 
              className="composer-input"
              placeholder="Ask about your documents, data, or collections..." 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isGenerating}
            />
            {isGenerating ? (
              <button type="button" onClick={handleCancel} className="button button-ghost" style={{ color: "var(--danger)" }}>
                Cancel
              </button>
            ) : (
              <button type="submit" className="button button-primary" style={{ borderRadius: "var(--radius-lg)" }}>
                Send
              </button>
            )}
          </div>
        </form>
      </div>

      <XRayPanel trace={debugTrace} onClose={() => setDebugTrace(null)} />
      <CitationModal 
        citation={activeCitation} 
        chunk={activeChunk} 
        onClose={() => { setActiveCitation(null); setActiveChunk(null); }} 
      />
    </div>
  );
}
