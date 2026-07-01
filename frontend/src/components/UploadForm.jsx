import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

function UploadForm({ collections, onUploadFile, onSubmitUrl }) {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [selectedCollection, setSelectedCollection] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [url, setUrl] = useState("");

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  async function handleFileSubmit(event) {
    event.preventDefault();
    if (!selectedFile) return;
    await onUploadFile({
      file: selectedFile,
      collectionId: selectedCollection,
    });
    setSelectedFile(null);
  }

  async function handleUrlSubmit(event) {
    event.preventDefault();
    if (!url) return;
    await onSubmitUrl({
      url,
      collectionIds: selectedCollection ? [selectedCollection] : [],
    });
    setUrl("");
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", marginBottom: "32px" }}>
      {/* Target Collection Select row */}
      <div className="panel glassmorphic" style={{ padding: "20px 24px", display: "flex", alignItems: "center", justifyContent: "space-between", gap: "24px", flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "14px", flex: "1 1 300px" }}>
          <div style={{
            width: "40px",
            height: "40px",
            borderRadius: "var(--radius-md)",
            background: "rgba(99, 91, 255, 0.1)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "20px",
            color: "var(--accent)"
          }}>
            📁
          </div>
          <div style={{ flex: 1 }}>
            <label htmlFor="collection-select" style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-secondary)", display: "block", marginBottom: "4px" }}>
              Target Collection
            </label>
            <select
              id="collection-select"
              value={selectedCollection}
              onChange={(e) => setSelectedCollection(e.target.value)}
              style={{
                border: "none",
                background: "transparent",
                fontSize: "15px",
                fontWeight: "600",
                padding: "2px 0",
                height: "auto",
                boxShadow: "none",
                color: "var(--text-primary)",
                width: "100%",
                cursor: "pointer",
                outline: "none"
              }}
            >
              <option value="">Default (Global Library)</option>
              {collections.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
        </div>
        
        {/* URL Fetch Tool */}
        <form onSubmit={handleUrlSubmit} style={{ display: "flex", gap: "10px", alignItems: "center", flex: "1 1 400px", maxWidth: "500px" }}>
          <input
            type="url"
            placeholder="Crawl website (e.g. https://example.com)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            style={{ height: "40px", fontSize: "13px", background: "rgba(255, 255, 255, 0.03)" }}
          />
          <button className="button button-primary" type="submit" disabled={!url} style={{ height: "40px", padding: "0 20px" }}>
            Fetch URL
          </button>
        </form>
      </div>

      {/* DRAG AND DROP ZONE */}
      <div 
        className="panel glassmorphic"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "48px 32px",
          border: dragOver ? "2px dashed var(--accent)" : "1px dashed var(--border-strong)",
          background: dragOver 
            ? "radial-gradient(circle at center, rgba(99, 91, 255, 0.08), rgba(99, 91, 255, 0.02))" 
            : "var(--glass-bg)",
          cursor: "pointer",
          textAlign: "center",
          minHeight: "240px",
          transition: "all var(--motion-base) var(--ease-standard)",
          boxShadow: dragOver ? "var(--shadow-glow)" : "var(--glass-shadow)"
        }}
        onClick={triggerFileSelect}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          style={{ display: "none" }} 
          accept=".pdf,.txt,.md,.markdown" 
        />
        <div style={{
          width: "64px",
          height: "64px",
          borderRadius: "50%",
          background: "rgba(99, 91, 255, 0.05)",
          border: "1px solid var(--glass-border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "28px",
          marginBottom: "20px",
          boxShadow: "var(--shadow-xs)"
        }}>
          ☁️
        </div>
        <h3 style={{ fontSize: "18px", fontWeight: "750", marginBottom: "8px", letterSpacing: "-0.02em" }}>
          Upload Source Document
        </h3>
        <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginBottom: "24px", maxWidth: "340px", lineHeight: "1.5" }}>
          Drag and drop PDF, Word, TXT, or markdown files here or <span style={{ color: "var(--accent)", fontWeight: "600", textDecoration: "underline" }}>browse local files</span>
        </p>
        
        {selectedFile ? (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "12px", width: "100%", maxWidth: "340px" }} onClick={e => e.stopPropagation()}>
            <div style={{ 
              fontSize: "13px", 
              fontWeight: "600", 
              color: "var(--text-primary)", 
              background: "rgba(255,255,255,0.03)", 
              border: "1px solid var(--border)",
              padding: "10px 14px", 
              borderRadius: "var(--radius-md)", 
              width: "100%", 
              textOverflow: "ellipsis", 
              overflow: "hidden", 
              whiteSpace: "nowrap" 
            }}>
              📄 {selectedFile.name}
            </div>
            <button 
              className="button button-primary" 
              onClick={handleFileSubmit} 
              style={{ width: "100%", height: "40px" }}
            >
              Start Ingestion Pipeline
            </button>
          </div>
        ) : (
          <button className="button button-ghost" style={{ height: "40px", padding: "0 24px" }}>
            Select Document
          </button>
        )}
      </div>

      {/* Action shortcut row */}
      <div style={{ display: "flex", justifyContent: "flex-end" }}>
        <button 
          className="button button-ghost glassmorphic" 
          style={{ 
            height: "48px", 
            padding: "0 24px", 
            borderRadius: "var(--radius-lg)", 
            border: "1px solid var(--glass-border)",
            boxShadow: "var(--glass-shadow)"
          }}
          onClick={() => navigate("/collections")}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <span>📁</span>
            <span style={{ fontWeight: "600", fontSize: "14px" }}>Manage Collections & Architecture</span>
          </div>
        </button>
      </div>
    </div>
  );
}

export default UploadForm;
