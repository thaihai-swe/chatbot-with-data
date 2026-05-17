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
  const [advancedConfig, setAdvancedConfig] = useState({
    enable_intelligence: true,
    enable_rewriting: true,
    enable_expansion: true,
    expansion_count: 3,
    enable_decomposition: true,
    enable_hyde: true,
    enable_synonym_expansion: true,
    enable_dynamic_routing: true,
    enable_reranking: true,
    enable_parent_child: true,
    });

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
                citations: turn.citations,
                chunks: turn.retrieved_chunks_json ? JSON.parse(turn.retrieved_chunks_json) : [],
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

    const cleanup = streamChatTurn(sid, text, advancedConfig, {
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
          return [...prev.slice(0, -1), { ...last, citations: data.citations, chunks: data.retrieved_chunks }];
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

  const toggleConfig = (key) => {
    setAdvancedConfig(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleCitationClick = (citation, chunks) => {
    const chunk = chunks.find(c => c.chunk_id === citation.chunk_id);
    if (chunk) {
      setActiveCitation(citation);
      setActiveChunk(chunk);
    }
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
              <h4 style={{ margin: "0 0 12px 0", fontSize: "12px", textTransform: "uppercase", color: "var(--text-muted)" }}>Retrieval Config</h4>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <label className="config-toggle">
                  <input type="checkbox" checked={advancedConfig.enable_intelligence} onChange={() => toggleConfig("enable_intelligence")} /> Intelligence
                </label>
                <label className="config-toggle">
                  <input type="checkbox" checked={advancedConfig.enable_rewriting} onChange={() => toggleConfig("enable_rewriting")} /> Intent Rewriting
                </label>
                <label className="config-toggle">
                  <input type="checkbox" checked={advancedConfig.enable_dynamic_routing} onChange={() => toggleConfig("enable_dynamic_routing")} /> Dynamic Routing
                </label>
                <label className="config-toggle">
                  <input type="checkbox" checked={advancedConfig.enable_expansion} onChange={() => toggleConfig("enable_expansion")} /> Query Expansion
                </label>
                <label className="config-toggle">
                  <input type="checkbox" checked={advancedConfig.enable_reranking} onChange={() => toggleConfig("enable_reranking")} /> Reranking
                </label>
                <label className="config-toggle">
                  <input type="checkbox" checked={advancedConfig.enable_parent_child} onChange={() => toggleConfig("enable_parent_child")} /> Parent-Child
                </label>
              </div>

              <h4 style={{ margin: "16px 0 12px 0", fontSize: "12px", textTransform: "uppercase", color: "var(--text-muted)", borderTop: "1px solid var(--border)", paddingTop: "12px" }}>Scope</h4>
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
              {msg.content}
              {debugMode && msg.trace && (
                <div style={{ marginTop: "12px" }}>
                  <button onClick={() => setDebugTrace(msg.trace)} className="button button-ghost" style={{ fontSize: "11px", height: "24px", padding: "0 8px", background: "var(--surface)" }}>
                    🔍 Pipeline X-Ray
                  </button>
                </div>
              )}
              {msg.citations && msg.citations.length > 0 && (
                <div className="citations-list">
                  <div style={{ fontSize: "12px", fontWeight: "600", marginBottom: "8px", color: "var(--text-muted)" }}>SOURCES</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                    {msg.citations.map((c, ci) => (
                      <span 
                        key={ci} 
                        className="citation-tag"
                        onClick={() => handleCitationClick(c, msg.chunks || [])}
                      >
                        {c.metadata?.title ? (c.metadata.title.length > 24 ? c.metadata.title.slice(0, 24) + '...' : c.metadata.title) : `Source ${c.chunk_id.slice(0,4)}`}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
          {statusMessage && (
            <div className="status-badge" style={{ alignSelf: "center", height: "28px" }}>
              {statusMessage}...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="chat-input-form">
          <div style={{ display: "flex", gap: "12px", maxWidth: "800px", margin: "0 auto", width: "100%" }}>
            <input 
              type="text" 
              placeholder="Ask a question..." 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isGenerating}
              style={{ flex: 1, height: "44px", borderRadius: "var(--radius-lg)" }}
            />
            {isGenerating ? (
              <button type="button" onClick={handleCancel} className="button button-danger" style={{ height: "44px" }}>
                Cancel
              </button>
            ) : (
              <button type="submit" className="button button-primary" style={{ height: "44px", padding: "0 24px" }}>
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
