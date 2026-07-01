import React, { useState, useEffect } from 'react';
import { getSettings, updateSettings } from '../api/settings';
import SettingsField from '../components/SettingsField';

const SettingsScreen = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [activeTab, setActiveTab] = useState('llm');

  useEffect(() => {
    fetchSettings();
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

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await updateSettings(settings);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="screen-container">Loading settings...</div>;
  if (error && !settings) return <div className="screen-container error">Error: {error}</div>;

  return (
    <div className="page-shell">
      <div className="dashboard-header">
        <div>
          <span className="eyebrow">Settings</span>
          <h1>System Configuration</h1>
          <p>Control the default behaviors for ingestion, hybrid retrieval pipelines, generation parameters, and guardrail safety shields.</p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {success && <div className="success-banner">Configuration saved successfully!</div>}

      <div className="settings-tabs" style={{ display: "flex", gap: "8px", marginBottom: "32px", borderBottom: "1px solid var(--border)", paddingBottom: "12px" }}>
        {[
          { id: "llm", label: "LLM & Generation" },
          { id: "retrieval", label: "Retrieval Settings" },
          { id: "ingestion", label: "Ingestion & Chunking" },
          { id: "safety", label: "Safety Shields" }
        ].map(tab => (
          <button
            key={tab.id}
            className={`button ${activeTab === tab.id ? 'button-primary' : 'button-ghost'}`}
            style={{ height: "40px", padding: "0 20px" }}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="settings-content" style={{ minHeight: "400px" }}>
        {/* LLM Settings */}
        {activeTab === 'llm' && (
          <section className="settings-section">
            <div className="panel glassmorphic">
              <h2 style={{ marginBottom: "24px", fontSize: "20px", fontWeight: "750", letterSpacing: "-0.02em" }}>LLM & Generation</h2>
              <SettingsField 
                label="Model" 
                description="The default chat model to use for query resolution."
              >
                <input 
                  type="text" 
                  value={settings.llm.model} 
                  onChange={(e) => handleUpdate('llm', 'model', e.target.value)}
                  style={{ width: "240px" }}
                />
              </SettingsField>
              <SettingsField 
                label="Temperature" 
                description="Controls model creativity / randomness (0.0 is deterministic, 1.0+ is creative)."
              >
                <input 
                  type="number" 
                  step="0.1" 
                  min="0" 
                  max="2"
                  value={settings.llm.temperature} 
                  onChange={(e) => handleUpdate('llm', 'temperature', parseFloat(e.target.value))}
                  style={{ width: "100px" }}
                />
              </SettingsField>
              <SettingsField 
                label="Streaming Mode" 
                description="Enable token-by-token text streaming for faster perceived response latency."
              >
                <label className="switch">
                  <input 
                    type="checkbox" 
                    checked={settings.llm.streaming_enabled} 
                    onChange={(e) => handleUpdate('llm', 'streaming_enabled', e.target.checked)}
                  />
                  <span className="slider"></span>
                </label>
              </SettingsField>
            </div>
          </section>
        )}

        {/* Retrieval Settings */}
        {activeTab === 'retrieval' && (
          <section className="settings-section">
            <div className="panel glassmorphic">
              <h2 style={{ marginBottom: "24px", fontSize: "20px", fontWeight: "750", letterSpacing: "-0.02em" }}>Retrieval Settings</h2>
              
              <SettingsField 
                label="Top K Chunks" 
                description="The maximum number of candidate text chunks to retrieve and inject into the prompt context."
              >
                <input 
                  type="number" 
                  min="1" 
                  max="100"
                  value={settings.retrieval.top_k} 
                  onChange={(e) => handleUpdate('retrieval', 'top_k', parseInt(e.target.value))}
                  style={{ width: "100px" }}
                />
              </SettingsField>
              
              <SettingsField 
                label="Retrieval Mode" 
                description="The search strategy to employ. Hybrid combines vector semantic embeddings and BM25 keyword matching."
              >
                <select 
                  value={settings.retrieval.retrieval_mode} 
                  onChange={(e) => handleUpdate('retrieval', 'retrieval_mode', e.target.value)}
                  style={{ width: "180px" }}
                >
                  <option value="semantic">Semantic Only</option>
                  <option value="keyword">Keyword Only</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </SettingsField>

              <h3 style={{ margin: "32px 0 16px", fontSize: "14px", fontWeight: "800", textTransform: "uppercase", letterSpacing: "0.15em", color: "var(--accent)", borderBottom: "1px solid var(--border)", paddingBottom: "10px" }}>
                Advanced Retrieval Pipelines
              </h3>
              
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "16px" }}>
                <SettingsField label="Intelligence (LLM Routing)" description="Use LLM to dynamically route or analyze search intents.">
                  <label className="switch">
                    <input type="checkbox" checked={settings.retrieval.intelligence_enabled} onChange={(e) => handleUpdate('retrieval', 'intelligence_enabled', e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </SettingsField>
                
                <SettingsField label="Dynamic Routing" description="Route queries to different strategies based on query intent classification.">
                  <label className="switch">
                    <input type="checkbox" checked={settings.retrieval.dynamic_routing_enabled} onChange={(e) => handleUpdate('retrieval', 'dynamic_routing_enabled', e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </SettingsField>

                <SettingsField label="Query Expansion" description="Generate query variations using an LLM to improve recall rates.">
                  <label className="switch">
                    <input type="checkbox" checked={settings.retrieval.query_expansion_enabled} onChange={(e) => handleUpdate('retrieval', 'query_expansion_enabled', e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </SettingsField>

                <SettingsField label="Query Decomposition" description="Decompose complex queries into simple sequential sub-questions.">
                  <label className="switch">
                    <input type="checkbox" checked={settings.retrieval.query_decomposition_enabled} onChange={(e) => handleUpdate('retrieval', 'query_decomposition_enabled', e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </SettingsField>

                <SettingsField label="HyDE (Hypothetical Doc)" description="Generate hypothetical answers to match against document embeddings.">
                  <label className="switch">
                    <input type="checkbox" checked={settings.retrieval.hyde_enabled} onChange={(e) => handleUpdate('retrieval', 'hyde_enabled', e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </SettingsField>

                <SettingsField label="Synonym Expansion" description="Expand abbreviations and domain synonyms dynamically.">
                  <label className="switch">
                    <input type="checkbox" checked={settings.retrieval.synonym_expansion_enabled} onChange={(e) => handleUpdate('retrieval', 'synonym_expansion_enabled', e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </SettingsField>

                <SettingsField label="Reranking" description="Use cross-encoders to re-evaluate and filter retrieved chunks.">
                  <label className="switch">
                    <input type="checkbox" checked={settings.retrieval.reranker_enabled} onChange={(e) => handleUpdate('retrieval', 'reranker_enabled', e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </SettingsField>

                <SettingsField label="Parent-Child Retrieval" description="Retrieve larger parent paragraphs for child token matches.">
                  <label className="switch">
                    <input type="checkbox" checked={settings.retrieval.parent_child_enabled} onChange={(e) => handleUpdate('retrieval', 'parent_child_enabled', e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </SettingsField>

                <SettingsField label="Multi-Hop Reasoning" description="Iteratively retrieve and synthesize context from multiple files.">
                  <label className="switch">
                    <input type="checkbox" checked={settings.retrieval.multi_hop_enabled} onChange={(e) => handleUpdate('retrieval', 'multi_hop_enabled', e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </SettingsField>

                <SettingsField label="Collection Routing" description="Dynamically route searches to target subsets of collections.">
                  <label className="switch">
                    <input type="checkbox" checked={settings.retrieval.collection_routing_enabled} onChange={(e) => handleUpdate('retrieval', 'collection_routing_enabled', e.target.checked)} />
                    <span className="slider"></span>
                  </label>
                </SettingsField>
              </div>
            </div>
          </section>
        )}

        {/* Ingestion Settings */}
        {activeTab === 'ingestion' && (
          <section className="settings-section">
            <div className="panel glassmorphic">
              <h2 style={{ marginBottom: "24px", fontSize: "20px", fontWeight: "750", letterSpacing: "-0.02em" }}>Ingestion & Chunking</h2>
              
              <SettingsField 
                label="Chunk Size (tokens)" 
                description="Target text chunk token length for embedding and indexing."
              >
                <input 
                  type="number" 
                  min="100" 
                  step="100"
                  value={settings.ingestion.chunk_size} 
                  onChange={(e) => handleUpdate('ingestion', 'chunk_size', parseInt(e.target.value))}
                  style={{ width: "120px" }}
                />
              </SettingsField>
              
              <SettingsField 
                label="Embedding Model" 
                description="The text embedding model used to vectorize files."
              >
                <input 
                  type="text" 
                  value={settings.ingestion.embedding_model} 
                  onChange={(e) => handleUpdate('ingestion', 'embedding_model', e.target.value)}
                  style={{ width: "240px" }}
                />
              </SettingsField>
              
              <SettingsField 
                label="Duplicate Detection" 
                description="Prevent uploading duplicate files by checking semantic similarity hashes."
              >
                <label className="switch">
                  <input 
                    type="checkbox" 
                    checked={settings.ingestion.duplicate_detection_enabled} 
                    onChange={(e) => handleUpdate('ingestion', 'duplicate_detection_enabled', e.target.checked)}
                  />
                  <span className="slider"></span>
                </label>
              </SettingsField>

              <h3 style={{ margin: "32px 0 16px", fontSize: "14px", fontWeight: "800", textTransform: "uppercase", letterSpacing: "0.15em", color: "var(--accent)", borderBottom: "1px solid var(--border)", paddingBottom: "10px" }}>
                Adaptive Tiering
              </h3>

              <SettingsField 
                label="Adaptive Tiering" 
                description="Index small documents entirely without chunking to retain full contextual flow."
              >
                <label className="switch">
                  <input 
                    type="checkbox" 
                    checked={settings.ingestion.adaptive_tiering_enabled} 
                    onChange={(e) => handleUpdate('ingestion', 'adaptive_tiering_enabled', e.target.checked)}
                  />
                  <span className="slider"></span>
                </label>
              </SettingsField>
              
              <SettingsField 
                label="Context Window Ratio" 
                description="Percentage of context window threshold to trigger adaptive tiering."
              >
                <div style={{ display: "flex", alignItems: "center", gap: "12px", width: "240px" }}>
                  <input 
                    type="range" 
                    min="0.1" 
                    max="1.0" 
                    step="0.05"
                    value={settings.ingestion.adaptive_tiering_ratio} 
                    onChange={(e) => handleUpdate('ingestion', 'adaptive_tiering_ratio', parseFloat(e.target.value))}
                    style={{ flex: 1, height: "6px" }}
                  />
                  <span className="mono" style={{ fontSize: "12px", width: "32px", textAlign: "right" }}>{settings.ingestion.adaptive_tiering_ratio}</span>
                </div>
              </SettingsField>
              
              <SettingsField 
                label="Explicit Token Threshold" 
                description="Hard token count limit for adaptive tiering. Set to 0 to use ratio instead."
              >
                <input 
                  type="number" 
                  min="0" 
                  step="1000"
                  value={settings.ingestion.adaptive_tiering_threshold ?? 0} 
                  onChange={(e) => handleUpdate('ingestion', 'adaptive_tiering_threshold', e.target.value ? parseInt(e.target.value) : null)}
                  style={{ width: "120px" }}
                />
              </SettingsField>
            </div>
          </section>
        )}

        {/* Safety Settings */}
        {activeTab === 'safety' && (
          <section className="settings-section">
            <div className="panel glassmorphic">
              <h2 style={{ marginBottom: "24px", fontSize: "20px", fontWeight: "750", letterSpacing: "-0.02em" }}>Safety Shields</h2>
              
              <SettingsField 
                label="Groundedness Check" 
                description="Validate LLM responses against retrieved sources to flag potential hallucinations."
              >
                <label className="switch">
                  <input 
                    type="checkbox" 
                    checked={settings.safety.groundedness_check_enabled} 
                    onChange={(e) => handleUpdate('safety', 'groundedness_check_enabled', e.target.checked)}
                  />
                  <span className="slider"></span>
                </label>
              </SettingsField>
              
              <SettingsField 
                label="Fuzzy Matching Injection Shield" 
                description="Use vector query distance to identify potential prompt injection attempts."
              >
                <label className="switch">
                  <input 
                    type="checkbox" 
                    checked={settings.safety.fuzzy_matching_enabled} 
                    onChange={(e) => handleUpdate('safety', 'fuzzy_matching_enabled', e.target.checked)}
                  />
                  <span className="slider"></span>
                </label>
              </SettingsField>
              
              <SettingsField 
                label="Injection Sensitivity Threshold" 
                description="Set similarity shield sensitivity. Lower values are stricter."
              >
                <div style={{ display: "flex", alignItems: "center", gap: "12px", width: "240px" }}>
                  <input 
                    type="range" 
                    min="0" 
                    max="1" 
                    step="0.1"
                    value={settings.safety.injection_risk_threshold} 
                    onChange={(e) => handleUpdate('safety', 'injection_risk_threshold', parseFloat(e.target.value))}
                    style={{ flex: 1, height: "6px" }}
                  />
                  <span className="mono" style={{ fontSize: "12px", width: "32px", textAlign: "right" }}>{settings.safety.injection_risk_threshold}</span>
                </div>
              </SettingsField>
            </div>
          </section>
        )}
      </div>

      <div className="settings-action-region glassmorphic" style={{ marginTop: "32px", padding: "16px 24px" }}>
        <button 
          className="button button-primary" 
          onClick={handleSave} 
          disabled={saving}
          style={{ height: "44px", padding: "0 32px" }}
        >
          {saving ? 'Saving Settings...' : 'Save Configuration'}
        </button>
      </div>
    </div>
  );
};

export default SettingsScreen;
