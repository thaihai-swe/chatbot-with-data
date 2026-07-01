import React, { useState, useEffect } from 'react';
import { getSettings, updateSettings } from '../api/settings';
import SettingsField from '../components/SettingsField';

const SettingsScreen = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);

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
          <p>Control the behavioral defaults for ingestion, retrieval, and generation.</p>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {success && <div className="success-banner">Settings saved successfully!</div>}

      <div className="settings-grid">
        {/* LLM Settings */}
        <section className="settings-section">
          <div className="panel" style={{ height: "100%" }}>
            <h2 style={{ marginBottom: "20px" }}>LLM & Generation</h2>
            <SettingsField 
              label="Model" 
              description="The default chat model to use."
            >
              <input 
                type="text" 
                value={settings.llm.model} 
                onChange={(e) => handleUpdate('llm', 'model', e.target.value)}
              />
            </SettingsField>
            <SettingsField 
              label="Temperature" 
              description="Control randomness (0.0 to 2.0)."
            >
              <input 
                type="number" 
                step="0.1" 
                min="0" 
                max="2"
                value={settings.llm.temperature} 
                onChange={(e) => handleUpdate('llm', 'temperature', parseFloat(e.target.value))}
              />
            </SettingsField>
            <SettingsField 
              label="Streaming" 
              description="Enable token-by-token generation."
            >
              <input 
                type="checkbox" 
                checked={settings.llm.streaming_enabled} 
                onChange={(e) => handleUpdate('llm', 'streaming_enabled', e.target.checked)}
              />
            </SettingsField>
          </div>
        </section>

        {/* Retrieval Settings */}
        <section className="settings-section">
          <div className="panel" style={{ height: "100%" }}>
            <h2 style={{ marginBottom: "20px" }}>Retrieval</h2>
            <SettingsField 
              label="Top K" 
              description="Number of chunks to retrieve per query."
            >
              <input 
                type="number" 
                min="1" 
                max="100"
                value={settings.retrieval.top_k} 
                onChange={(e) => handleUpdate('retrieval', 'top_k', parseInt(e.target.value))}
              />
            </SettingsField>
            <SettingsField 
              label="Retrieval Mode" 
              description="Strategy for finding relevant chunks."
            >
              <select 
                value={settings.retrieval.retrieval_mode} 
                onChange={(e) => handleUpdate('retrieval', 'retrieval_mode', e.target.value)}
              >
                <option value="semantic">Semantic Only</option>
                <option value="keyword">Keyword Only</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </SettingsField>

            <h3 style={{ margin: "24px 0 16px", fontSize: "14px", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>Advanced Retrieval</h3>
            
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <SettingsField label="Intelligence (LLM Routing)" description="Enable LLM to classify and process queries.">
                <input type="checkbox" checked={settings.retrieval.intelligence_enabled} onChange={(e) => handleUpdate('retrieval', 'intelligence_enabled', e.target.checked)} />
              </SettingsField>
              
              <SettingsField label="Dynamic Routing" description="Route queries to different strategies based on classification.">
                <input type="checkbox" checked={settings.retrieval.dynamic_routing_enabled} onChange={(e) => handleUpdate('retrieval', 'dynamic_routing_enabled', e.target.checked)} />
              </SettingsField>

              <SettingsField label="Query Expansion" description="Generate variations of the query.">
                <input type="checkbox" checked={settings.retrieval.query_expansion_enabled} onChange={(e) => handleUpdate('retrieval', 'query_expansion_enabled', e.target.checked)} />
              </SettingsField>

              <SettingsField label="Query Decomposition" description="Break complex queries into sub-questions.">
                <input type="checkbox" checked={settings.retrieval.query_decomposition_enabled} onChange={(e) => handleUpdate('retrieval', 'query_decomposition_enabled', e.target.checked)} />
              </SettingsField>

              <SettingsField label="HyDE" description="Hypothetical Document Embeddings for better semantic matching.">
                <input type="checkbox" checked={settings.retrieval.hyde_enabled} onChange={(e) => handleUpdate('retrieval', 'hyde_enabled', e.target.checked)} />
              </SettingsField>

              <SettingsField label="Synonym Expansion" description="Identify and expand domain-specific synonyms.">
                <input type="checkbox" checked={settings.retrieval.synonym_expansion_enabled} onChange={(e) => handleUpdate('retrieval', 'synonym_expansion_enabled', e.target.checked)} />
              </SettingsField>

              <SettingsField label="Reranking" description="Use a cross-encoder to rerank retrieved chunks.">
                <input type="checkbox" checked={settings.retrieval.reranker_enabled} onChange={(e) => handleUpdate('retrieval', 'reranker_enabled', e.target.checked)} />
              </SettingsField>

              <SettingsField label="Parent-Child Retrieval" description="Retrieve larger parent context when a child chunk is found.">
                <input type="checkbox" checked={settings.retrieval.parent_child_enabled} onChange={(e) => handleUpdate('retrieval', 'parent_child_enabled', e.target.checked)} />
              </SettingsField>

              <SettingsField label="Multi-Hop Reasoning" description="Enable iterative reasoning across multiple documents.">
                <input type="checkbox" checked={settings.retrieval.multi_hop_enabled} onChange={(e) => handleUpdate('retrieval', 'multi_hop_enabled', e.target.checked)} />
              </SettingsField>

              <SettingsField label="Collection Routing" description="Dynamically route queries to specific collections.">
                <input type="checkbox" checked={settings.retrieval.collection_routing_enabled} onChange={(e) => handleUpdate('retrieval', 'collection_routing_enabled', e.target.checked)} />
              </SettingsField>
            </div>

          </div>
        </section>

        {/* Ingestion Settings */}
        <section className="settings-section">
          <div className="panel" style={{ height: "100%" }}>
            <h2 style={{ marginBottom: "20px" }}>Ingestion & Chunking</h2>
            <SettingsField 
              label="Chunk Size" 
              description="Target size of each text chunk."
            >
              <input 
                type="number" 
                min="100" 
                step="100"
                value={settings.ingestion.chunk_size} 
                onChange={(e) => handleUpdate('ingestion', 'chunk_size', parseInt(e.target.value))}
              />
            </SettingsField>
            <SettingsField 
              label="Embedding Model" 
              description="The model to use for vector embeddings."
            >
              <input 
                type="text" 
                value={settings.ingestion.embedding_model} 
                onChange={(e) => handleUpdate('ingestion', 'embedding_model', e.target.value)}
              />
            </SettingsField>
            <SettingsField 
              label="Duplicate Detection" 
              description="Check for existing documents during ingestion."
            >
              <input 
                type="checkbox" 
                checked={settings.ingestion.duplicate_detection_enabled} 
                onChange={(e) => handleUpdate('ingestion', 'duplicate_detection_enabled', e.target.checked)}
              />
            </SettingsField>

            <h3 style={{ margin: "24px 0 16px", fontSize: "14px", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>Adaptive Tiering</h3>

            <SettingsField 
              label="Adaptive Tiering" 
              description="Inject small documents whole instead of chunking them."
            >
              <input 
                type="checkbox" 
                checked={settings.ingestion.adaptive_tiering_enabled} 
                onChange={(e) => handleUpdate('ingestion', 'adaptive_tiering_enabled', e.target.checked)}
              />
            </SettingsField>
            <SettingsField 
              label="Context Window Ratio" 
              description="Fraction of LLM context window used as threshold (0.1–1.0). Ignored when explicit threshold is set."
            >
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <input 
                  type="range" 
                  min="0.1" 
                  max="1.0" 
                  step="0.05"
                  value={settings.ingestion.adaptive_tiering_ratio} 
                  onChange={(e) => handleUpdate('ingestion', 'adaptive_tiering_ratio', parseFloat(e.target.value))}
                  style={{ flex: 1 }}
                />
                <span className="mono" style={{ fontSize: "12px", width: "32px" }}>{settings.ingestion.adaptive_tiering_ratio}</span>
              </div>
            </SettingsField>
            <SettingsField 
              label="Explicit Threshold (tokens)" 
              description="Set an exact token threshold. Overrides ratio when > 0. Leave 0 to use ratio."
            >
              <input 
                type="number" 
                min="0" 
                step="1000"
                value={settings.ingestion.adaptive_tiering_threshold ?? 0} 
                onChange={(e) => handleUpdate('ingestion', 'adaptive_tiering_threshold', e.target.value ? parseInt(e.target.value) : null)}
              />
            </SettingsField>
          </div>
        </section>

        {/* Safety Settings */}
        <section className="settings-section">
          <div className="panel" style={{ height: "100%" }}>
            <h2 style={{ marginBottom: "20px" }}>Safety</h2>
            <SettingsField 
              label="Groundedness Check" 
              description="Verify answers against retrieved sources."
            >
              <input 
                type="checkbox" 
                checked={settings.safety.groundedness_check_enabled} 
                onChange={(e) => handleUpdate('safety', 'groundedness_check_enabled', e.target.checked)}
              />
            </SettingsField>
            <SettingsField 
              label="Fuzzy Matching Detection" 
              description="Use embeddings to detect semantic prompt injections."
            >
              <input 
                type="checkbox" 
                checked={settings.safety.fuzzy_matching_enabled} 
                onChange={(e) => handleUpdate('safety', 'fuzzy_matching_enabled', e.target.checked)}
              />
            </SettingsField>
            <SettingsField 
              label="Injection Threshold" 
              description="Sensitivity of injection detection."
            >
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <input 
                  type="range" 
                  min="0" 
                  max="1" 
                  step="0.1"
                  value={settings.safety.injection_risk_threshold} 
                  onChange={(e) => handleUpdate('safety', 'injection_risk_threshold', parseFloat(e.target.value))}
                  style={{ flex: 1 }}
                />
                <span className="mono" style={{ fontSize: "12px", width: "24px" }}>{settings.safety.injection_risk_threshold}</span>
              </div>
            </SettingsField>
          </div>
        </section>
      </div>

      <div className="settings-action-region">
        <button 
          className="button button-primary" 
          onClick={handleSave} 
          disabled={saving}
          style={{ height: "48px", padding: "0 32px" }}
        >
          {saving ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>
    </div>
  );
};

export default SettingsScreen;
