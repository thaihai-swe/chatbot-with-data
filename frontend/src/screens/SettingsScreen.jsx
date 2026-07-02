import React, { useState, useEffect } from 'react';
import { getSettings, updateSettings } from '../api/settings';

const SettingsScreen = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  
  // Left Navigation Active Category: General, model-rag, security-safety, integrations, api-keys, billing, team
  const [activeCategory, setActiveCategory] = useState('model-rag');

  // Local storage backup for mockup simulation settings
  const [mockSettings, setMockSettings] = useState({
    fine_tuning: false,
    max_tokens: 1024,
    top_p: 0.90,
    presence_penalty: 0.3,
    context_awareness: true,
    hardware_acceleration: true,
    max_context_length: 32000,
    reranker_model: "bge-reranker-v2-m3",
    project_api_key: "***************************g4X",
    model_provider_key: "***************************f7R",
    prompt_injection_checker: true,
    pii_redaction: true,
    anonymization_level: "High",
  });

  useEffect(() => {
    fetchSettings();
    const saved = localStorage.getItem("mockSettings");
    if (saved) {
      try {
        setMockSettings(prev => ({
          ...prev,
          ...JSON.parse(saved)
        }));
      } catch (e) {
        console.error("Failed to load mock settings", e);
      }
    }
  }, []);

  const fetchSettings = async () => {
    try {
      const data = await getSettings();
      setSettings(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleUpdate = (section, key, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
    setSuccess(false);
  };

  const handleMockUpdate = (key, value) => {
    setMockSettings(prev => ({
      ...prev,
      [key]: value
    }));
    setSuccess(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await updateSettings(settings);
      localStorage.setItem("mockSettings", JSON.stringify(mockSettings));
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleRevokeKey = (keyName) => {
    handleMockUpdate(keyName, "");
    alert(`${keyName === 'project_api_key' ? 'Project' : 'Model Provider'} API Key revoked.`);
  };

  const handleUpdateKey = (keyName) => {
    const newVal = prompt(`Enter new value for ${keyName === 'project_api_key' ? 'Project' : 'Model Provider'} API Key:`);
    if (newVal !== null) {
      // Mask key for mockup purposes, but keep last characters visible
      const masked = "*".repeat(27) + newVal.slice(-3);
      handleMockUpdate(keyName, masked);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert("API Key copied to clipboard!");
  };

  if (loading) return <div className="page-shell"><div className="empty-state"><div className="spinner" />Loading settings...</div></div>;
  if (error && !settings) return <div className="page-shell"><div className="error-banner">Error loading settings: {error}</div></div>;

  const accentColor = "#00d992"; // Electric green accent

  return (
    <div className="page-shell" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      
      {error && <div className="error-banner" style={{ margin: 0 }}>{error}</div>}
      {success && <div className="success-banner" style={{ margin: 0 }}>Configuration saved successfully!</div>}

      {/* Dual Column Layout: Left Sidebar, Right Panel Workspace */}
      <div style={{ display: "grid", gridTemplateColumns: "220px 1fr", gap: "24px", alignItems: "start" }}>
        
        {/* Left Column: Settings Sidebar */}
        <div 
          className="panel glassmorphic" 
          style={{ 
            padding: "16px", 
            display: "flex", 
            flexDirection: "column", 
            gap: "8px",
            borderRadius: "var(--radius-lg)",
            border: "1px solid var(--border)",
            minHeight: "400px"
          }}
        >
          <div style={{ padding: "0 12px 12px 12px", borderBottom: "1px solid var(--border)" }}>
            <span style={{ fontSize: "11px", fontWeight: "800", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
              Control Panel
            </span>
            <h3 style={{ fontSize: "14px", fontWeight: "750", margin: "2px 0 0 0", color: "var(--text-primary)" }}>
              Settings
            </h3>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            {[
              { id: "general", label: "General", emoji: "⚙️" },
              { id: "model-rag", label: "Model & RAG", emoji: "🧠" },
              { id: "security-safety", label: "Security & Safety", emoji: "🛡️" },
              { id: "integrations", label: "Integrations", emoji: "🔌" },
              { id: "api-keys", label: "API Keys", emoji: "🔑" },
              { id: "billing", label: "Billing", emoji: "💳" },
              { id: "team", label: "Team", emoji: "👥" }
            ].map((cat) => {
              const isActive = activeCategory === cat.id;
              return (
                <div
                  key={cat.id}
                  onClick={() => setActiveCategory(cat.id)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "10px 14px",
                    cursor: "pointer",
                    borderRadius: "var(--radius-md)",
                    background: isActive ? "rgba(255, 255, 255, 0.04)" : "transparent",
                    color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                    fontWeight: isActive ? "700" : "500",
                    fontSize: "13px",
                    transition: "all var(--motion-fast) var(--ease-standard)"
                  }}
                  className="sources-collection-header-row"
                >
                  <span style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span>{cat.emoji}</span>
                    <span>{cat.label}</span>
                  </span>
                  
                  {isActive && (
                    <span style={{
                      width: "6px",
                      height: "6px",
                      borderRadius: "50%",
                      background: accentColor,
                      boxShadow: `0 0 8px ${accentColor}`
                    }} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Settings Workspace */}
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          
          {/* CATEGORY: MODEL & RAG (Main screen from mockup) */}
          {activeCategory === 'model-rag' && (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div style={{ borderBottom: "1px solid var(--border)", paddingBottom: "12px" }}>
                <h2 style={{ fontSize: "20px", fontWeight: "750", margin: 0, color: "var(--text-primary)" }}>
                  Model & RAG Settings
                </h2>
                <p style={{ margin: "4px 0 0 0", color: "var(--text-secondary)", fontSize: "13px" }}>
                  Fine-tune RAG chunking limits, vector scoring parameters, and primary LLM model configuration.
                </p>
              </div>

              {/* 1. RAG Configuration Card */}
              <div className="panel glassmorphic" style={{ padding: "24px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "20px" }}>
                <h3 style={{ margin: 0, fontSize: "14px", fontWeight: "750", color: "var(--text-primary)", borderBottom: "1px solid var(--border)", paddingBottom: "10px" }}>
                  RAG Configuration
                </h3>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px 24px" }}>
                  {/* Chunk Size */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    <label htmlFor="chunk-size-input" style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>
                      Chunk Size (tokens)
                    </label>
                    <input 
                      id="chunk-size-input"
                      type="number" 
                      min="100" 
                      step="100"
                      value={settings.ingestion.chunk_size} 
                      onChange={(e) => handleUpdate('ingestion', 'chunk_size', parseInt(e.target.value))}
                      style={{ 
                        height: "40px", 
                        background: "var(--background)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius-md)",
                        padding: "0 12px",
                        color: "var(--text-primary)"
                      }}
                    />
                  </div>

                  {/* Chunk Overlap */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    <label htmlFor="chunk-overlap-input" style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>
                      Chunk Overlap (tokens)
                    </label>
                    <input 
                      id="chunk-overlap-input"
                      type="number" 
                      min="10" 
                      step="10"
                      value={settings.ingestion.chunk_overlap} 
                      onChange={(e) => handleUpdate('ingestion', 'chunk_overlap', parseInt(e.target.value))}
                      style={{ 
                        height: "40px", 
                        background: "var(--background)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius-md)",
                        padding: "0 12px",
                        color: "var(--text-primary)"
                      }}
                    />
                  </div>

                  {/* Reranker Model Selection */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    <label htmlFor="reranker-select" style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>
                      Reranker Model
                    </label>
                    <select
                      id="reranker-select"
                      value={mockSettings.reranker_model}
                      onChange={(e) => handleMockUpdate('reranker_model', e.target.value)}
                      style={{ 
                        height: "40px", 
                        background: "var(--background)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius-md)",
                        padding: "0 12px",
                        color: "var(--text-primary)"
                      }}
                    >
                      <option value="bge-reranker-v2-m3">bge-reranker-v2-m3</option>
                      <option value="cohere-rerank-v3">cohere-rerank-v3-english</option>
                      <option value="none">Disabled (No Rerank)</option>
                    </select>
                  </div>

                  {/* Temperature Slider */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>
                      <label htmlFor="temperature-range">Temperature</label>
                      <span className="mono" style={{ color: accentColor, fontWeight: "700" }}>{settings.llm.temperature.toFixed(1)}</span>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "12px", height: "40px" }}>
                      <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>0.0</span>
                      <input 
                        id="temperature-range"
                        type="range" 
                        min="0.0" 
                        max="1.0" 
                        step="0.1"
                        value={settings.llm.temperature} 
                        onChange={(e) => handleUpdate('llm', 'temperature', parseFloat(e.target.value))}
                        style={{ 
                          flex: 1, 
                          height: "6px",
                          accentColor: accentColor 
                        }}
                      />
                      <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>1.0</span>
                    </div>
                  </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px 24px", borderTop: "1px solid var(--border)", paddingTop: "16px", marginTop: "4px" }}>
                  {/* Primary LLM Model */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    <label htmlFor="primary-llm-select" style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>Primary LLM Model</label>
                    <select
                      id="primary-llm-select"
                      value={settings.llm.model}
                      onChange={(e) => handleUpdate('llm', 'model', e.target.value)}
                      style={{ 
                        height: "40px", 
                        background: "var(--background)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius-md)",
                        padding: "0 12px",
                        color: "var(--text-primary)"
                      }}
                    >
                      <option value="gpt-4o">Hyperion Pro v4.2 (gpt-4o)</option>
                      <option value="gpt-4">GPT-4 Turbo</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Legacy</option>
                      <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    </select>
                  </div>

                  {/* Retrieval Mode */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    <label htmlFor="retrieval-mode-select" style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>Retrieval Mode</label>
                    <select 
                      id="retrieval-mode-select"
                      value={settings.retrieval.retrieval_mode} 
                      onChange={(e) => handleUpdate('retrieval', 'retrieval_mode', e.target.value)}
                      style={{ 
                        height: "40px", 
                        background: "var(--background)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius-md)",
                        padding: "0 12px",
                        color: "var(--text-primary)"
                      }}
                    >
                      <option value="semantic">Semantic Only</option>
                      <option value="keyword">Keyword Only</option>
                      <option value="hybrid">Hybrid (Keyword + Semantic)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* 2. API Keys Card */}
              <div className="panel glassmorphic" style={{ padding: "24px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "16px" }}>
                <h3 style={{ margin: 0, fontSize: "14px", fontWeight: "750", color: "var(--text-primary)", borderBottom: "1px solid var(--border)", paddingBottom: "10px" }}>
                  API Keys
                </h3>

                <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
                  {/* Project API Key */}
                  <div style={{ display: "flex", alignItems: "center", gap: "16px", justifyContent: "space-between" }}>
                    <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "4px" }}>
                      <span style={{ fontSize: "12.5px", fontWeight: "600", color: "var(--text-primary)" }}>Project API Key</span>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", position: "relative" }}>
                        <input 
                          type="text" 
                          readOnly 
                          value={mockSettings.project_api_key}
                          style={{ 
                            height: "36px", 
                            background: "var(--surface-muted)", 
                            border: "1px solid var(--border)",
                            borderRadius: "var(--radius-md)",
                            padding: "0 36px 0 12px",
                            fontFamily: "var(--font-mono)",
                            fontSize: "12px",
                            color: "var(--text-secondary)",
                            width: "100%",
                            maxWidth: "280px"
                          }}
                        />
                        <button 
                          onClick={() => copyToClipboard(mockSettings.project_api_key)}
                          style={{
                            background: "transparent",
                            border: "none",
                            cursor: "pointer",
                            fontSize: "12px",
                            padding: "4px",
                            position: "absolute",
                            left: "250px"
                          }}
                          title="Copy Key"
                        >
                          📋
                        </button>
                        <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>Hidden</span>
                      </div>
                    </div>
                    <button 
                      className="button button-danger"
                      onClick={() => handleRevokeKey("project_api_key")}
                      style={{ height: "36px", padding: "0 16px", fontSize: "12px", borderRadius: "var(--radius-md)" }}
                    >
                      revoke
                    </button>
                  </div>

                  {/* Model Provider Key */}
                  <div style={{ display: "flex", alignItems: "center", gap: "16px", justifyContent: "space-between", borderTop: "1px solid var(--border)", paddingTop: "14px" }}>
                    <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "4px" }}>
                      <span style={{ fontSize: "12.5px", fontWeight: "600", color: "var(--text-primary)" }}>Model Provider Key</span>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", position: "relative" }}>
                        <input 
                          type="text" 
                          readOnly 
                          value={mockSettings.model_provider_key}
                          style={{ 
                            height: "36px", 
                            background: "var(--surface-muted)", 
                            border: "1px solid var(--border)",
                            borderRadius: "var(--radius-md)",
                            padding: "0 36px 0 12px",
                            fontFamily: "var(--font-mono)",
                            fontSize: "12px",
                            color: "var(--text-secondary)",
                            width: "100%",
                            maxWidth: "280px"
                          }}
                        />
                        <button 
                          onClick={() => copyToClipboard(mockSettings.model_provider_key)}
                          style={{
                            background: "transparent",
                            border: "none",
                            cursor: "pointer",
                            fontSize: "12px",
                            padding: "4px",
                            position: "absolute",
                            left: "250px"
                          }}
                          title="Copy Key"
                        >
                          📋
                        </button>
                        <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>Hidden</span>
                      </div>
                    </div>
                    <button 
                      className="button button-secondary"
                      onClick={() => handleUpdateKey("model_provider_key")}
                      style={{ height: "36px", padding: "0 16px", fontSize: "12px", border: "1px solid var(--border-strong)", borderRadius: "var(--radius-md)" }}
                    >
                      update
                    </button>
                  </div>
                </div>
              </div>

              {/* 3. Security & Safety Card */}
              <div className="panel glassmorphic" style={{ padding: "24px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "20px" }}>
                <h3 style={{ margin: 0, fontSize: "14px", fontWeight: "750", color: "var(--text-primary)", borderBottom: "1px solid var(--border)", paddingBottom: "10px" }}>
                  Security & Safety
                </h3>

                <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                  {/* Strict Prompt Injection Checker */}
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <div>
                      <span style={{ fontSize: "13px", fontWeight: "650", color: "var(--text-primary)", display: "block" }}>
                        Strict Prompt Injection Checker
                      </span>
                      <span style={{ fontSize: "11.5px", color: "var(--text-secondary)", display: "block", marginTop: "2px" }}>
                        Prevent malicious inputs from overriding system instructions
                      </span>
                    </div>
                    <label className="switch">
                      <input 
                        type="checkbox" 
                        checked={mockSettings.prompt_injection_checker} 
                        onChange={(e) => handleMockUpdate('prompt_injection_checker', e.target.checked)}
                      />
                      <span className="slider" style={{ background: mockSettings.prompt_injection_checker ? accentColor : "" }}></span>
                    </label>
                  </div>

                  {/* PII Redaction */}
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", borderTop: "1px solid var(--border)", paddingTop: "14px" }}>
                    <div>
                      <span style={{ fontSize: "13px", fontWeight: "650", color: "var(--text-primary)", display: "block" }}>
                        PII Redaction
                      </span>
                      <span style={{ fontSize: "11.5px", color: "var(--text-secondary)", display: "block", marginTop: "2px" }}>
                        Automatically redact PII (names, emails, phones) from outputs
                      </span>
                    </div>
                    <label className="switch">
                      <input 
                        type="checkbox" 
                        checked={mockSettings.pii_redaction} 
                        onChange={(e) => handleMockUpdate('pii_redaction', e.target.checked)}
                      />
                      <span className="slider" style={{ background: mockSettings.pii_redaction ? accentColor : "" }}></span>
                    </label>
                  </div>

                  {/* Anonymization Level Dropdown */}
                  <div style={{ display: "flex", flexDirection: "column", gap: "6px", borderTop: "1px solid var(--border)", paddingTop: "14px" }}>
                    <label htmlFor="anonymization-select" style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>
                      Anonymization Level
                    </label>
                    <select
                      id="anonymization-select"
                      value={mockSettings.anonymization_level}
                      onChange={(e) => handleMockUpdate('anonymization_level', e.target.value)}
                      style={{ 
                        height: "40px", 
                        background: "var(--background)", 
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius-md)",
                        padding: "0 12px",
                        color: "var(--text-primary)",
                        width: "100%",
                        maxWidth: "340px"
                      }}
                    >
                      <option value="Low">Low (Fuzzy Redaction)</option>
                      <option value="Medium">Medium (Regex Rules)</option>
                      <option value="High">High (Strict Entity Scopes)</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* CATEGORY: SECURITY & SAFETY DETAILS */}
          {activeCategory === 'security-safety' && (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div style={{ borderBottom: "1px solid var(--border)", paddingBottom: "12px" }}>
                <h2 style={{ fontSize: "20px", fontWeight: "750", margin: 0, color: "var(--text-primary)" }}>
                  Security Guards & Safety Shields
                </h2>
                <p style={{ margin: "4px 0 0 0", color: "var(--text-secondary)", fontSize: "13px" }}>
                  Prevent prompt engineering exploits and run citation verification grounding.
                </p>
              </div>

              <div className="panel glassmorphic" style={{ padding: "24px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "20px" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <div>
                    <span style={{ fontSize: "13px", fontWeight: "650", color: "var(--text-primary)", display: "block" }}>Groundedness Verification</span>
                    <span style={{ fontSize: "11.5px", color: "var(--text-secondary)", display: "block", marginTop: "2px" }}>Validate generated answers against retrieved sources to flag hallucinations.</span>
                  </div>
                  <label className="switch">
                    <input 
                      type="checkbox" 
                      checked={settings.safety.groundedness_check_enabled} 
                      onChange={(e) => handleUpdate('safety', 'groundedness_check_enabled', e.target.checked)}
                    />
                    <span className="slider" style={{ background: settings.safety.groundedness_check_enabled ? accentColor : "" }}></span>
                  </label>
                </div>

                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", borderTop: "1px solid var(--border)", paddingTop: "14px" }}>
                  <div>
                    <span style={{ fontSize: "13px", fontWeight: "650", color: "var(--text-primary)", display: "block" }}>Fuzzy Matching Injection Shield</span>
                    <span style={{ fontSize: "11.5px", color: "var(--text-secondary)", display: "block", marginTop: "2px" }}>Analyze query prompt similarity distance to block prompt injections.</span>
                  </div>
                  <label className="switch">
                    <input 
                      type="checkbox" 
                      checked={settings.safety.fuzzy_matching_enabled} 
                      onChange={(e) => handleUpdate('safety', 'fuzzy_matching_enabled', e.target.checked)}
                    />
                    <span className="slider" style={{ background: settings.safety.fuzzy_matching_enabled ? accentColor : "" }}></span>
                  </label>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: "8px", borderTop: "1px solid var(--border)", paddingTop: "14px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>
                    <label htmlFor="injection-threshold-range">Injection Sensitivity Threshold</label>
                    <span className="mono" style={{ color: accentColor, fontWeight: "700" }}>{settings.safety.injection_risk_threshold}</span>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                    <input 
                      id="injection-threshold-range"
                      type="range" 
                      min="0" 
                      max="1" 
                      step="0.1"
                      value={settings.safety.injection_risk_threshold} 
                      onChange={(e) => handleUpdate('safety', 'injection_risk_threshold', parseFloat(e.target.value))}
                      style={{ flex: 1, height: "6px", accentColor: accentColor }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* CATEGORY: GENERAL SETTINGS */}
          {activeCategory === 'general' && (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div style={{ borderBottom: "1px solid var(--border)", paddingBottom: "12px" }}>
                <h2 style={{ fontSize: "20px", fontWeight: "750", margin: 0, color: "var(--text-primary)" }}>
                  General System Settings
                </h2>
                <p style={{ margin: "4px 0 0 0", color: "var(--text-secondary)", fontSize: "13px" }}>
                  Configure background parameters and system execution options.
                </p>
              </div>

              <div className="panel glassmorphic" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px", padding: "24px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)" }}>
                <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                  <span className="eyebrow" style={{ fontSize: "10px", color: "var(--accent)" }}>System Status</span>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "50%", background: "var(--success)" }} />
                    <span style={{ fontSize: "15px", fontWeight: "700" }}>Active / Online</span>
                  </div>
                  <p style={{ fontSize: "12.5px", color: "var(--text-secondary)", margin: 0 }}>All pipelines are operational.</p>
                </div>
                
                <div style={{ display: "flex", flexDirection: "column", gap: "8px", borderLeft: "1px solid var(--border)", paddingLeft: "20px" }}>
                  <span className="eyebrow" style={{ fontSize: "10px", color: "var(--accent)" }}>Active Model Resolver</span>
                  <div style={{ fontSize: "15px", fontWeight: "700" }}>
                    {settings.llm.model}
                  </div>
                  <p style={{ fontSize: "12.5px", color: "var(--text-secondary)", margin: 0 }}>Default model mapped for queries.</p>
                </div>
              </div>

              <div className="panel glassmorphic" style={{ padding: "24px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "16px" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span style={{ fontSize: "13px", fontWeight: "650", color: "var(--text-primary)" }}>Enable Streaming Responses</span>
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={settings.llm.streaming_enabled}
                      onChange={(e) => handleUpdate('llm', 'streaming_enabled', e.target.checked)}
                    />
                    <span className="slider" style={{ background: settings.llm.streaming_enabled ? accentColor : "" }}></span>
                  </label>
                </div>

                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", borderTop: "1px solid var(--border)", paddingTop: "14px" }}>
                  <span style={{ fontSize: "13px", fontWeight: "650", color: "var(--text-primary)" }}>Fine-Tuning Enabled</span>
                  <label className="switch">
                    <input
                      type="checkbox"
                      checked={mockSettings.fine_tuning}
                      onChange={(e) => handleMockUpdate('fine_tuning', e.target.checked)}
                    />
                    <span className="slider" style={{ background: mockSettings.fine_tuning ? accentColor : "" }}></span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* CATEGORY: API KEYS SPECIFIC PANEL */}
          {activeCategory === 'api-keys' && (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div style={{ borderBottom: "1px solid var(--border)", paddingBottom: "12px" }}>
                <h2 style={{ fontSize: "20px", fontWeight: "750", margin: 0, color: "var(--text-primary)" }}>
                  API Keys Dashboard
                </h2>
                <p style={{ margin: "4px 0 0 0", color: "var(--text-secondary)", fontSize: "13px" }}>
                  Manage authorization tokens and model provider keys securely.
                </p>
              </div>

              <div className="panel glassmorphic" style={{ padding: "24px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "14px" }}>
                {/* Project Key */}
                <div style={{ display: "flex", alignItems: "center", gap: "16px", justifyContent: "space-between" }}>
                  <div style={{ flex: 1 }}>
                    <span style={{ fontSize: "13px", fontWeight: "650", color: "var(--text-primary)", display: "block" }}>Project API Key</span>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginTop: "2px" }}>Used for API requests authorization.</span>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "8px" }}>
                      <input 
                        type="text" 
                        readOnly 
                        value={mockSettings.project_api_key}
                        style={{ 
                          height: "36px", 
                          background: "var(--surface-muted)", 
                          border: "1px solid var(--border)",
                          borderRadius: "var(--radius-md)",
                          padding: "0 12px",
                          fontFamily: "var(--font-mono)",
                          fontSize: "12px",
                          color: "var(--text-secondary)",
                          width: "280px"
                        }}
                      />
                      <button className="button button-ghost" style={{ height: "36px", padding: "0 12px" }} onClick={() => copyToClipboard(mockSettings.project_api_key)}>Copy</button>
                    </div>
                  </div>
                  <button className="button button-danger" style={{ height: "36px", padding: "0 16px" }} onClick={() => handleRevokeKey("project_api_key")}>Revoke</button>
                </div>

                {/* Model Provider Key */}
                <div style={{ display: "flex", alignItems: "center", gap: "16px", justifyContent: "space-between", borderTop: "1px solid var(--border)", paddingTop: "16px" }}>
                  <div style={{ flex: 1 }}>
                    <span style={{ fontSize: "13px", fontWeight: "650", color: "var(--text-primary)", display: "block" }}>Model Provider API Key</span>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginTop: "2px" }}>Used for LLM generation requests.</span>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "8px" }}>
                      <input 
                        type="text" 
                        readOnly 
                        value={mockSettings.model_provider_key}
                        style={{ 
                          height: "36px", 
                          background: "var(--surface-muted)", 
                          border: "1px solid var(--border)",
                          borderRadius: "var(--radius-md)",
                          padding: "0 12px",
                          fontFamily: "var(--font-mono)",
                          fontSize: "12px",
                          color: "var(--text-secondary)",
                          width: "280px"
                        }}
                      />
                      <button className="button button-ghost" style={{ height: "36px", padding: "0 12px" }} onClick={() => copyToClipboard(mockSettings.model_provider_key)}>Copy</button>
                    </div>
                  </div>
                  <button className="button button-secondary" style={{ height: "36px", padding: "0 16px", border: "1px solid var(--border-strong)" }} onClick={() => handleUpdateKey("model_provider_key")}>Update</button>
                </div>
              </div>
            </div>
          )}

          {/* CATEGORIES PLACEHOLDERS: INTEGRATIONS, BILLING, TEAM */}
          {(activeCategory === 'integrations' || activeCategory === 'billing' || activeCategory === 'team') && (
            <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
              <div style={{ borderBottom: "1px solid var(--border)", paddingBottom: "12px" }}>
                <h2 style={{ fontSize: "20px", fontWeight: "750", margin: 0, color: "var(--text-primary)" }}>
                  {activeCategory === 'integrations' && "System Integrations"}
                  {activeCategory === 'billing' && "Billing & Subscription"}
                  {activeCategory === 'team' && "Team & Collaborators"}
                </h2>
                <p style={{ margin: "4px 0 0 0", color: "var(--text-secondary)", fontSize: "13px" }}>
                  {activeCategory === 'integrations' && "Connect Weaviate, SQLite, and external storage endpoints."}
                  {activeCategory === 'billing' && "Manage payment profiles, invoice archives, and token consumption logs."}
                  {activeCategory === 'team' && "Configure permissions and coordinate seats across project scopes."}
                </p>
              </div>

              <div className="panel glassmorphic" style={{ padding: "40px", textAlign: "center", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)" }}>
                <div style={{ fontSize: "32px", marginBottom: "12px" }}>
                  {activeCategory === 'integrations' && "🔌"}
                  {activeCategory === 'billing' && "💳"}
                  {activeCategory === 'team' && "👥"}
                </div>
                <h3 style={{ fontSize: "15px", fontWeight: "750", margin: "0 0 6px 0", color: "var(--text-primary)" }}>
                  {activeCategory === 'integrations' && "Integrations Console"}
                  {activeCategory === 'billing' && "Billing Dashboard"}
                  {activeCategory === 'team' && "Team Access Control"}
                </h3>
                <p style={{ fontSize: "12.5px", color: "var(--text-secondary)", margin: 0, maxWidth: "340px", marginLeft: "auto", marginRight: "auto" }}>
                  This dashboard is managed by organization administrative credentials. Contact organization owners to modify billing tiers, configure databases, or manage team tokens.
                </p>
              </div>
            </div>
          )}

          {/* Action buttons (Save Settings) */}
          <div 
            className="panel glassmorphic" 
            style={{ 
              display: "flex", 
              justifyContent: "flex-end", 
              padding: "16px 24px", 
              borderRadius: "var(--radius-lg)", 
              border: "1px solid var(--border)" 
            }}
          >
            <button 
              className="button button-primary" 
              onClick={handleSave} 
              disabled={saving}
              style={{ 
                height: "40px", 
                padding: "0 28px",
                background: accentColor,
                color: "black",
                fontWeight: "700",
                border: "none",
                borderRadius: "var(--radius-md)",
                cursor: "pointer"
              }}
            >
              {saving ? 'Saving Settings...' : 'Save Configuration'}
            </button>
          </div>

        </div>

      </div>

    </div>
  );
};

export default SettingsScreen;
