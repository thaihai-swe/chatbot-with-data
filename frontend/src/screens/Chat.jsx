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
                trace: turn.retrieval_trace,
                evaluation: turn.evaluation_metrics
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
      onCitations: (citations) => {
        setMessages(prev => {
          if (prev.length === 0) return prev;
          const last = prev[prev.length - 1];
          if (last.role !== "assistant") return prev;
          return [...prev.slice(0, -1), { ...last, citations }];
        });
      },
      onTrace: (trace) => {
        setMessages(prev => {
          if (prev.length === 0) return prev;
          const last = prev[prev.length - 1];
          if (last.role !== "assistant") return prev;
          return [...prev.slice(0, -1), { ...last, trace: trace.retrieval, evaluation: trace.evaluation }];
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

  return (
    <div className="chat-container">
      <aside className="chat-sidebar">
        <button onClick={handleCreateSession} className="button" style={{ width: "100%", marginBottom: "20px" }}>
          + New Chat
        </button>
        <button onClick={() => setShowSettings(!showSettings)} className="button button-outline" style={{ width: "100%", marginBottom: "20px" }}>
          {showSettings ? "Hide Advanced Settings" : "Advanced Settings"}
        </button>
        
        {showSettings && (
          <div style={{ marginBottom: "20px", fontSize: "0.8rem", background: "var(--color-bg)", padding: "10px", borderRadius: "8px" }}>
            <h4 style={{ margin: "0 0 10px 0" }}>Retrieval Config</h4>
            <label style={{ display: "flex", alignItems: "center", marginBottom: "6px", cursor: "pointer" }}>
              <input type="checkbox" style={{ width: "auto", marginRight: "8px" }} checked={advancedConfig.enable_intelligence} onChange={() => toggleConfig("enable_intelligence")} /> Intelligence (Classify)
            </label>
            <label style={{ display: "flex", alignItems: "center", marginBottom: "6px", cursor: "pointer" }}>
              <input type="checkbox" style={{ width: "auto", marginRight: "8px" }} checked={advancedConfig.enable_rewriting} onChange={() => toggleConfig("enable_rewriting")} /> Intent Rewriting
            </label>
            <label style={{ display: "flex", alignItems: "center", marginBottom: "6px", cursor: "pointer" }}>
              <input type="checkbox" style={{ width: "auto", marginRight: "8px" }} checked={advancedConfig.enable_dynamic_routing} onChange={() => toggleConfig("enable_dynamic_routing")} /> Dynamic Routing
            </label>
            <label style={{ display: "flex", alignItems: "center", marginBottom: "6px", cursor: "pointer" }}>
              <input type="checkbox" style={{ width: "auto", marginRight: "8px" }} checked={advancedConfig.enable_expansion} onChange={() => toggleConfig("enable_expansion")} /> Query Expansion
            </label>
            <label style={{ display: "flex", alignItems: "center", marginBottom: "6px", cursor: "pointer" }}>
              <input type="checkbox" style={{ width: "auto", marginRight: "8px" }} checked={advancedConfig.enable_decomposition} onChange={() => toggleConfig("enable_decomposition")} /> Decomposition
            </label>
            <label style={{ display: "flex", alignItems: "center", marginBottom: "6px", cursor: "pointer" }}>
              <input type="checkbox" style={{ width: "auto", marginRight: "8px" }} checked={advancedConfig.enable_hyde} onChange={() => toggleConfig("enable_hyde")} /> HyDE
            </label>
            <label style={{ display: "flex", alignItems: "center", marginBottom: "6px", cursor: "pointer" }}>
              <input type="checkbox" style={{ width: "auto", marginRight: "8px" }} checked={advancedConfig.enable_synonym_expansion} onChange={() => toggleConfig("enable_synonym_expansion")} /> Synonyms
            </label>
            <label style={{ display: "flex", alignItems: "center", marginBottom: "6px", cursor: "pointer" }}>
              <input type="checkbox" style={{ width: "auto", marginRight: "8px" }} checked={advancedConfig.enable_reranking} onChange={() => toggleConfig("enable_reranking")} /> Reranking
            </label>
            <label style={{ display: "flex", alignItems: "center", marginBottom: "6px", cursor: "pointer" }}>
              <input type="checkbox" style={{ width: "auto", marginRight: "8px" }} checked={advancedConfig.enable_parent_child} onChange={() => toggleConfig("enable_parent_child")} /> Parent-Child
            </label>

            <h4 style={{ margin: "15px 0 10px 0", borderTop: "1px solid rgba(0,0,0,0.05)", paddingTop: "10px" }}>Scope Collections</h4>
            <div style={{ maxHeight: "150px", overflowY: "auto", border: "1px solid rgba(0,0,0,0.1)", borderRadius: "4px", padding: "8px", background: "rgba(255,255,255,0.3)" }}>
              {availableCollections.length === 0 && <div style={{ opacity: 0.5, fontSize: "0.7rem" }}>No collections available</div>}
              {availableCollections.map(c => (
                <label key={c.id} style={{ display: "flex", alignItems: "center", marginBottom: "6px", cursor: "pointer" }}>
                  <input 
                    type="checkbox" 
                    style={{ width: "auto", marginRight: "8px" }}
                    checked={selectedCollections.includes(c.id)} 
                    onChange={() => handleToggleCollection(c.id)} 
                  /> 
                  <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.name}</span>
                </label>
              ))}
            </div>
            <div style={{ marginTop: "8px", fontSize: "0.7rem", opacity: 0.7 }}>
              {selectedCollections.length === 0 ? "Searching all collections" : `Searching ${selectedCollections.length} selected collections`}
            </div>
          </div>
        )}

        <div className="session-list">
          {sessions.map(s => (
            <div key={s.id} 
                onClick={() => navigate(`/chat/${s.id}`)}
                className={`session-item ${sessionId === s.id ? "session-item-active" : ""}`}>
              <div style={{ flex: 1 }}>
                <div className="mono" style={{ fontSize: "0.75rem", opacity: 0.8 }}>{s.id.slice(0, 8)}</div>
                <div style={{ fontSize: "0.7rem", marginTop: "4px" }}>{new Date(s.created_at).toLocaleString()}</div>
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
            <div style={{ color: "#888", textAlign: "center", marginTop: "100px", maxWidth: "400px", margin: "100px auto" }}>
              <p>Select a session or start typing to begin a conversation with your document knowledge base.</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-bubble ${msg.role === "user" ? "message-user" : "message-assistant"}`}>
              {msg.content}
              {msg.trace && (
                <div style={{ marginTop: "10px" }}>
                  <button onClick={() => setDebugTrace(msg.trace)} className="button button-outline" style={{ fontSize: "0.7rem", padding: "2px 8px" }}>
                    🔍 View Trace
                  </button>
                </div>
              )}
              {msg.citations && msg.citations.length > 0 && (
                <div className="citations-list">
                  <strong>Sources:</strong>
                  <div style={{ marginTop: "6px" }}>
                    {msg.citations.map((c, ci) => (
                      <span key={ci} className="citation-tag">
                        {c.metadata?.title ? (c.metadata.title.length > 20 ? c.metadata.title.slice(0, 20) + '...' : c.metadata.title) : `Source ${c.chunk_id.slice(0,4)}`}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
          {statusMessage && (
            <div className="mono" style={{ fontSize: "0.75rem", color: "#666", alignSelf: "center", background: "rgba(0,0,0,0.05)", padding: "4px 12px", borderRadius: "999px" }}>
              {statusMessage}...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="chat-input-form">
          <input 
            type="text" 
            className="input" 
            placeholder="Ask a question about your documents..." 
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isGenerating}
            style={{ flex: 1 }}
          />
          {isGenerating ? (
            <button type="button" onClick={handleCancel} className="button button-danger">
              Cancel
            </button>
          ) : (
            <button type="submit" className="button">
              Send
            </button>
          )}
        </form>
      </div>

      {debugTrace && (
        <div style={{
          position: "absolute", top: 0, right: 0, bottom: 0, width: "400px", 
          background: "white", borderLeft: "1px solid var(--color-border)",
          boxShadow: "-2px 0 10px rgba(0,0,0,0.1)", zIndex: 100, overflowY: "auto"
        }}>
          <div style={{ padding: "20px", display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--color-border)" }}>
            <h3 style={{ margin: 0 }}>Retrieval Trace</h3>
            <button onClick={() => setDebugTrace(null)} className="button button-outline" style={{ padding: "4px 8px" }}>Close</button>
          </div>
          <div style={{ padding: "20px" }}>
            {debugTrace.retrieval?.transformations?.rewritten_query && (
              <div style={{ marginBottom: "15px", padding: "10px", background: "rgba(0,123,255,0.05)", borderRadius: "6px", border: "1px solid rgba(0,123,255,0.1)" }}>
                <div style={{ fontSize: "0.7rem", fontWeight: "bold", textTransform: "uppercase", marginBottom: "4px", color: "#007bff" }}>Cleaned Intent</div>
                <div style={{ fontSize: "0.85rem" }}>{debugTrace.retrieval.transformations.rewritten_query}</div>
              </div>
            )}
            <pre className="mono" style={{ fontSize: "0.75rem", whiteSpace: "pre-wrap", background: "var(--color-bg)", padding: "10px", borderRadius: "8px" }}>
              {JSON.stringify(debugTrace, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
