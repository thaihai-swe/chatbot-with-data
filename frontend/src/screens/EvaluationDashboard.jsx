import React, { useState, useEffect } from "react";
import { listDatasets, listRuns, saveDataset, triggerRun } from "../api/eval";
import RunDetail from "../components/RunDetail";
import ExperimentComparison from "../components/ExperimentComparison";

export default function EvaluationDashboard() {
  const [activeTab, setActiveTab] = useState("runs"); // runs, datasets, comparison
  const [datasets, setDatasets] = useState([]);
  const [runs, setRuns] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingDataset, setEditingDataset] = useState(null);
  const [showRunConfig, setShowRunConfig] = useState(null); // datasetId to run
  const [selectedRun, setSelectedRun] = useState(null);

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      if (activeTab === "datasets") {
        const data = await listDatasets();
        setDatasets(data);
      } else if (activeTab === "runs") {
        const data = await listRuns();
        setRuns(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveDataset = async (dataset) => {
    try {
      await saveDataset(dataset);
      setEditingDataset(null);
      fetchData();
    } catch (err) {
      alert("Failed to save dataset: " + err.message);
    }
  };

  const handleTriggerRun = async (datasetId, config) => {
    try {
      await triggerRun(datasetId, config);
      setShowRunConfig(null);
      setActiveTab("runs");
    } catch (err) {
      alert("Failed to trigger run: " + err.message);
    }
  };

  return (
    <div className="container" style={{ padding: "40px 20px" }}>
      <header style={{ marginBottom: "30px" }}>
        <h1 style={{ margin: 0, fontSize: "2.2rem" }}>Evaluation & Observability</h1>
        <p style={{ color: "rgba(255,255,255,0.7)" }}>Measure, compare, and improve your RAG pipeline.</p>
      </header>

      <div className="card" style={{ padding: "0" }}>
        <div style={{ display: "flex", borderBottom: "1px solid var(--color-border)" }}>
          <button 
            className={`tab-button ${activeTab === "runs" ? "active" : ""}`}
            onClick={() => setActiveTab("runs")}
            style={tabStyle(activeTab === "runs")}
          >
            Experiment Runs
          </button>
          <button 
            className={`tab-button ${activeTab === "datasets" ? "active" : ""}`}
            onClick={() => setActiveTab("datasets")}
            style={tabStyle(activeTab === "datasets")}
          >
            Datasets
          </button>
          <button 
            className={`tab-button ${activeTab === "comparison" ? "active" : ""}`}
            onClick={() => setActiveTab("comparison")}
            style={tabStyle(activeTab === "comparison")}
          >
            Comparison
          </button>
        </div>

        <div style={{ padding: "20px" }}>
          {error && (
            <div style={{ padding: "10px", background: "rgba(255,0,0,0.1)", color: "#ff4d4d", borderRadius: "6px", marginBottom: "20px" }}>
              Error: {error}
            </div>
          )}

          {activeTab === "runs" && (
            selectedRun ? (
              <RunDetail run={selectedRun} onBack={() => setSelectedRun(null)} />
            ) : (
              <RunsList runs={runs} isLoading={isLoading} onRefresh={fetchData} onViewDetail={setSelectedRun} />
            )
          )}

          {activeTab === "datasets" && (
            <DatasetsList 
              datasets={datasets} 
              isLoading={isLoading} 
              onRefresh={fetchData} 
              onEdit={setEditingDataset}
              onRun={setShowRunConfig}
            />
          )}

          {activeTab === "comparison" && (
            <ExperimentComparison runs={runs} />
          )}
        </div>
      </div>

      {editingDataset && (
        <DatasetEditor 
          dataset={editingDataset} 
          onSave={handleSaveDataset} 
          onCancel={() => setEditingDataset(null)} 
        />
      )}

      {showRunConfig && (
        <RunConfigModal 
          datasetId={showRunConfig}
          onRun={handleTriggerRun}
          onCancel={() => setShowRunConfig(null)}
        />
      )}
    </div>
  );
}

function RunsList({ runs, isLoading, onRefresh, onViewDetail }) {
  if (isLoading) return <div className="mono">Loading runs...</div>;
  if (runs.length === 0) return <div>No evaluation runs found.</div>;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px" }}>
        <h3 style={{ margin: 0 }}>Recent Experiments</h3>
        <button className="button button-outline" style={{ padding: "4px 12px" }} onClick={onRefresh}>Refresh</button>
      </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "2px solid var(--color-border)" }}>
              <th style={{ padding: "10px" }}>Run ID</th>
              <th style={{ padding: "10px" }}>Dataset</th>
              <th style={{ padding: "10px" }}>Status</th>
              <th style={{ padding: "10px" }}>Groundedness</th>
              <th style={{ padding: "10px" }}>Relevance</th>
              <th style={{ padding: "10px" }}>Hit Rate</th>
              <th style={{ padding: "10px" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {runs.map(run => (
              <tr key={run.id} style={{ borderBottom: "1px solid var(--color-border)" }}>
                <td style={{ padding: "10px" }} className="mono">{run.id}</td>
                <td style={{ padding: "10px" }}>{run.dataset_id}</td>
                <td style={{ padding: "10px" }}>
                  <span style={{ 
                    padding: "2px 8px", borderRadius: "999px", fontSize: "0.7rem",
                    background: run.status === "completed" ? "rgba(0,255,0,0.1)" : "rgba(255,255,0,0.1)",
                    color: run.status === "completed" ? "#4CAF50" : "#FFC107"
                  }}>
                    {run.status}
                  </span>
                </td>
                <td style={{ padding: "10px" }}>{run.metrics_summary?.avg_groundedness?.toFixed(2) || "-"}</td>
                <td style={{ padding: "10px" }}>{run.metrics_summary?.avg_relevance?.toFixed(2) || "-"}</td>
                <td style={{ padding: "10px" }}>{run.metrics_summary?.hit_rate !== undefined ? `${(run.metrics_summary.hit_rate * 100).toFixed(0)}%` : "-"}</td>
                <td style={{ padding: "10px" }}>
                  <button className="button button-outline" onClick={() => onViewDetail(run)} style={{ fontSize: "0.7rem", padding: "2px 8px" }}>View Details</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DatasetsList({ datasets, isLoading, onRefresh, onEdit, onRun }) {
  if (isLoading) return <div className="mono">Loading datasets...</div>;
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "15px" }}>
        <h3 style={{ margin: 0 }}>Available Datasets</h3>
        <button className="button" style={{ padding: "4px 12px" }} onClick={() => onEdit({ id: "new_dataset", name: "New Dataset", cases: [] })}>
          + New Dataset
        </button>
      </div>
      {datasets.length === 0 ? (
        <div>No datasets found. Create one to start evaluating.</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "20px" }}>
          {datasets.map(ds => (
            <div key={ds.id} className="card" style={{ background: "rgba(255,255,255,0.05)" }}>
              <h4>{ds.name}</h4>
              <p style={{ fontSize: "0.8rem", color: "rgba(255,255,255,0.6)" }}>{ds.description || "No description"}</p>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "15px" }}>
                <span style={{ fontSize: "0.75rem" }}>{ds.cases.length} Cases</span>
                <div style={{ display: "flex", gap: "10px" }}>
                  <button className="button button-outline" onClick={() => onEdit(ds)} style={{ fontSize: "0.7rem", padding: "2px 8px" }}>Edit</button>
                  <button className="button" onClick={() => onRun(ds.id)} style={{ fontSize: "0.7rem", padding: "2px 8px" }}>Run</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function DatasetEditor({ dataset, onSave, onCancel }) {
  const [jsonValue, setJsonValue] = useState(JSON.stringify(dataset, null, 2));
  const [parseError, setParseError] = useState(null);

  const handleSave = () => {
    try {
      const parsed = JSON.parse(jsonValue);
      onSave(parsed);
    } catch (err) {
      setParseError(err.message);
    }
  };

  return (
    <div style={modalOverlayStyle}>
      <div className="card" style={{ width: "800px", maxWidth: "90vw", maxHeight: "90vh", display: "flex", flexDirection: "column" }}>
        <h3>Edit Dataset: {dataset.id}</h3>
        {parseError && <div style={{ color: "#ff4d4d", fontSize: "0.8rem", marginBottom: "10px" }}>JSON Error: {parseError}</div>}
        <textarea 
          className="mono"
          style={{ flex: 1, minHeight: "400px", background: "var(--color-bg)", color: "var(--color-text)", padding: "10px", borderRadius: "6px", border: "1px solid var(--color-border)" }}
          value={jsonValue}
          onChange={(e) => {
            setJsonValue(e.target.value);
            setParseError(null);
          }}
        />
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "15px", marginTop: "20px" }}>
          <button className="button button-outline" onClick={onCancel}>Cancel</button>
          <button className="button" onClick={handleSave}>Save Dataset</button>
        </div>
      </div>
    </div>
  );
}

function RunConfigModal({ datasetId, onRun, onCancel }) {
  const [config, setConfig] = useState({
    enable_intelligence: false,
    enable_rewriting: false,
    enable_expansion: false,
    expansion_count: 3,
    enable_hyde: false,
    enable_reranking: false,
  });

  return (
    <div style={modalOverlayStyle}>
      <div className="card" style={{ width: "500px", maxWidth: "90vw" }}>
        <h3>Evaluation Config</h3>
        <p style={{ fontSize: "0.8rem", marginBottom: "20px" }}>Dataset: <span className="mono">{datasetId}</span></p>
        
        <div style={{ display: "grid", gap: "12px" }}>
          <ConfigToggle label="Query Intelligence" checked={config.enable_intelligence} onChange={(v) => setConfig({...config, enable_intelligence: v})} />
          <ConfigToggle label="Query Rewriting" checked={config.enable_rewriting} onChange={(v) => setConfig({...config, enable_rewriting: v})} />
          <ConfigToggle label="Query Expansion" checked={config.enable_expansion} onChange={(v) => setConfig({...config, enable_expansion: v})} />
          <ConfigToggle label="HyDE" checked={config.enable_hyde} onChange={(v) => setConfig({...config, enable_hyde: v})} />
          <ConfigToggle label="Reranking" checked={config.enable_reranking} onChange={(v) => setConfig({...config, enable_reranking: v})} />
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: "15px", marginTop: "30px" }}>
          <button className="button button-outline" onClick={onCancel}>Cancel</button>
          <button className="button" onClick={() => onRun(datasetId, config)}>Start Evaluation</button>
        </div>
      </div>
    </div>
  );
}

function ConfigToggle({ label, checked, onChange }) {
  return (
    <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer" }}>
      <span style={{ fontSize: "0.9rem" }}>{label}</span>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
    </label>
  );
}

const tabStyle = (isActive) => ({
  padding: "15px 25px",
  background: isActive ? "rgba(255,255,255,0.05)" : "transparent",
  border: "none",
  borderBottom: isActive ? "2px solid var(--color-primary)" : "none",
  color: isActive ? "var(--color-primary)" : "var(--color-text)",
  cursor: "pointer",
  fontSize: "0.9rem",
  fontWeight: isActive ? "bold" : "normal",
  transition: "all 0.2s"
});

const modalOverlayStyle = {
  position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
  background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000
};
