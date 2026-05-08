import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { 
  createChatSession, 
  listChatSessions, 
  getChatHistory, 
  streamChatTurn,
  cancelChatTurn
} from "../api/chat";

export default function ChatScreen() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [sessions, setChatSessions] = useState([]);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [activeTurnId, setActiveTurnId] = useState(null);
  const messagesEndRef = useRef(null);

  const [showSettings, setShowSettings] = useState(false);
  const [advancedConfig, setAdvancedConfig] = useState({
    enable_intelligence: false,
    enable_expansion: false,
    expansion_count: 3,
    enable_decomposition: false,
    enable_hyde: false,
    enable_synonym_expansion: false,
    enable_dynamic_routing: false,
    enable_reranking: false,
    enable_parent_child: false,
    auto_collection_detection: false
  });
  const [debugTrace, setDebugTrace] = useState(null);

  // Load sessions
  useEffect(() => {
    listChatSessions().then(setChatSessions).catch(console.error);
  }, []);

  // Load history when sessionId changes
  useEffect(() => {
    if (sessionId) {
      getChatHistory(sessionId)
        .then(history => {
          const formatted = [];
          history.forEach(turn => {
            formatted.push({ role: "user", content: turn.query_text });
            if (turn.answer_text) {
              formatted.push({ 
                role: "assistant", 
                content: turn.answer_text,
                citations: turn.citations,
                trace: turn.retrieval_trace
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
      const session = await createChatSession();
      setChatSessions([session, ...sessions]);
      navigate(`/chat/${session.id}`);
    } catch (err) {
      alert("Failed to create session");
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isGenerating) return;

    if (!sessionId) {
      // Auto-create session if none selected
      const session = await createChatSession();
      setChatSessions([session, ...sessions]);
      navigate(`/chat/${session.id}`);
      _submitMessage(session.id, inputValue);
    } else {
      _submitMessage(sessionId, inputValue);
    }
    
    setInputValue("");
  };

  const _submitMessage = (sid, text) => {
    setMessages(prev => [...prev, { role: "user", content: text }]);
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
          const last = prev[prev.length - 1];
          const updated = [...prev.slice(0, -1), { ...last, content: last.content + token }];
          return updated;
        });
      },
      onCitations: (citations) => {
        setMessages(prev => {
          const last = prev[prev.length - 1];
          return [...prev.slice(0, -1), { ...last, citations }];
        });
      },
      onTrace: (trace) => {
        setMessages(prev => {
          const last = prev[prev.length - 1];
          return [...prev.slice(0, -1), { ...last, trace }];
        });
      },
      onError: (err) => {
        setStatusMessage(`Error: ${err.message}`);
        setIsGenerating(false);
      },
      onDone: () => {
        setMessages(prev => {
          const last = prev[prev.length - 1];
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
            <label style={{ display: "block", marginBottom: "6px" }}>
              <input type="checkbox" checked={advancedConfig.enable_intelligence} onChange={() => toggleConfig("enable_intelligence")} /> Intelligence (Classify)
            </label>
            <label style={{ display: "block", marginBottom: "6px" }}>
              <input type="checkbox" checked={advancedConfig.enable_dynamic_routing} onChange={() => toggleConfig("enable_dynamic_routing")} /> Dynamic Routing
            </label>
            <label style={{ display: "block", marginBottom: "6px" }}>
              <input type="checkbox" checked={advancedConfig.enable_expansion} onChange={() => toggleConfig("enable_expansion")} /> Query Expansion
            </label>
            <label style={{ display: "block", marginBottom: "6px" }}>
              <input type="checkbox" checked={advancedConfig.enable_decomposition} onChange={() => toggleConfig("enable_decomposition")} /> Decomposition
            </label>
            <label style={{ display: "block", marginBottom: "6px" }}>
              <input type="checkbox" checked={advancedConfig.enable_hyde} onChange={() => toggleConfig("enable_hyde")} /> HyDE
            </label>
            <label style={{ display: "block", marginBottom: "6px" }}>
              <input type="checkbox" checked={advancedConfig.enable_synonym_expansion} onChange={() => toggleConfig("enable_synonym_expansion")} /> Synonyms
            </label>
            <label style={{ display: "block", marginBottom: "6px" }}>
              <input type="checkbox" checked={advancedConfig.enable_reranking} onChange={() => toggleConfig("enable_reranking")} /> Reranking
            </label>
            <label style={{ display: "block", marginBottom: "6px" }}>
              <input type="checkbox" checked={advancedConfig.enable_parent_child} onChange={() => toggleConfig("enable_parent_child")} /> Parent-Child
            </label>
            <label style={{ display: "block", marginBottom: "6px" }}>
              <input type="checkbox" checked={advancedConfig.auto_collection_detection} onChange={() => toggleConfig("auto_collection_detection")} /> Auto Collection
            </label>
          </div>
        )}

        <div className="session-list">
          {sessions.map(s => (
            <div key={s.id} 
                onClick={() => navigate(`/chat/${s.id}`)}
                className={`session-item ${sessionId === s.id ? "session-item-active" : ""}`}>
              <div className="mono" style={{ fontSize: "0.75rem", opacity: 0.8 }}>{s.id.slice(0, 8)}</div>
              <div style={{ fontSize: "0.7rem", marginTop: "4px" }}>{new Date(s.created_at).toLocaleString()}</div>
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
            <pre className="mono" style={{ fontSize: "0.75rem", whiteSpace: "pre-wrap", background: "var(--color-bg)", padding: "10px", borderRadius: "8px" }}>
              {JSON.stringify(debugTrace, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
