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
    <div className="screen-container">
      <div className="screen-header">
        <h1>System Configuration</h1>
        <p>Control the behavioral defaults for ingestion, retrieval, and generation.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {success && <div className="success-banner">Settings saved successfully!</div>}

      <div className="settings-grid">
        {/* LLM Settings */}
        <section className="settings-section card">
          <h2>LLM & Generation</h2>
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
        </section>

        {/* Retrieval Settings */}
        <section className="settings-section card">
          <h2>Retrieval</h2>
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
        </section>

        {/* Ingestion Settings */}
        <section className="settings-section card">
          <h2>Ingestion & Chunking</h2>
          <SettingsField 
            label="Chunk Size" 
            description="Target size of each text chunk (tokens/chars)."
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
            label="Duplicate Detection" 
            description="Check for existing documents during ingestion."
          >
            <input 
              type="checkbox" 
              checked={settings.ingestion.duplicate_detection_enabled} 
              onChange={(e) => handleUpdate('ingestion', 'duplicate_detection_enabled', e.target.checked)}
            />
          </SettingsField>
        </section>

        {/* Safety Settings */}
        <section className="settings-section card">
          <h2>Safety</h2>
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
            label="Injection Risk Threshold" 
            description="Sensitivity of prompt-injection detection."
          >
            <input 
              type="range" 
              min="0" 
              max="1" 
              step="0.1"
              value={settings.safety.injection_risk_threshold} 
              onChange={(e) => handleUpdate('safety', 'injection_risk_threshold', parseFloat(e.target.value))}
            />
            <span>{settings.safety.injection_risk_threshold}</span>
          </SettingsField>
        </section>
      </div>

      <div className="settings-actions">
        <button 
          className="btn btn-primary" 
          onClick={handleSave} 
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>
    </div>
  );
};

export default SettingsScreen;
