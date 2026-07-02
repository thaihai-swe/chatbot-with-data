import { useState, useRef } from "react";

function UploadForm({ activeCollectionId, onUploadFile, onSubmitUrl }) {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [showUrlForm, setShowUrlForm] = useState(false);
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
      collectionId: activeCollectionId || "",
    });
    setSelectedFile(null);
  }

  async function handleUrlSubmit(event) {
    event.preventDefault();
    if (!url) return;
    await onSubmitUrl({
      url,
      collectionIds: activeCollectionId ? [activeCollectionId] : [],
    });
    setUrl("");
    setShowUrlForm(false);
  }

  const accentColor = "#00d992"; // Electric green from mockup

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px", width: "100%" }}>
      {/* COMPACT DRAG & DROP FILE ZONE */}
      <div 
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        style={{
          display: "flex",
          alignItems: "center",
          gap: "16px",
          padding: "16px 20px",
          border: `1.5px dashed ${dragOver ? "var(--accent)" : accentColor}`,
          borderRadius: "var(--radius-lg)",
          background: dragOver 
            ? "rgba(0, 217, 146, 0.06)" 
            : "rgba(0, 217, 146, 0.01)",
          cursor: "pointer",
          transition: "all var(--motion-base) var(--ease-standard)",
          position: "relative"
        }}
        onClick={triggerFileSelect}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          style={{ display: "none" }} 
          accept=".pdf,.txt,.md,.markdown,.docx,.doc,.csv,.xlsx,.xls" 
        />
        
        {/* Upload Icon */}
        <div style={{
          width: "36px",
          height: "36px",
          borderRadius: "50%",
          background: "rgba(0, 217, 146, 0.08)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "18px",
          color: accentColor,
          flexShrink: 0
        }}>
          📤
        </div>

        {/* Text Instructions */}
        <div style={{ flex: 1, minWidth: 0, textAlign: "left" }}>
          <h4 style={{ fontSize: "13px", fontWeight: "700", color: accentColor, margin: "0 0 2px 0" }}>
            Upload Files
          </h4>
          <p style={{ fontSize: "11px", color: "var(--text-secondary)", margin: 0, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
            Drag & Drop Files Here or Click to Browse
          </p>
          <span style={{ fontSize: "9px", color: "var(--text-muted)", display: "block", marginTop: "1px" }}>
            Supports PDFs, CSVs, TXT, DOCX
          </span>
        </div>
      </div>

      {/* Action panel when file is staged */}
      {selectedFile && (
        <div 
          style={{ 
            display: "flex", 
            alignItems: "center", 
            gap: "10px", 
            padding: "8px 12px", 
            background: "var(--surface-muted)", 
            border: "1px solid var(--border)",
            borderRadius: "var(--radius-md)",
            marginTop: "4px"
          }}
        >
          <span style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-primary)", flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            Staged: {selectedFile.name}
          </span>
          <button 
            className="button button-primary" 
            onClick={handleFileSubmit} 
            style={{ 
              height: "28px", 
              fontSize: "11px", 
              padding: "0 12px", 
              borderRadius: "var(--radius-xs)",
              background: accentColor,
              color: "black",
              fontWeight: "700",
              border: "none",
              cursor: "pointer"
            }}
          >
            Upload
          </button>
          <button 
            className="button button-ghost" 
            onClick={() => setSelectedFile(null)} 
            style={{ height: "28px", fontSize: "11px", padding: "0 8px", color: "var(--danger)" }}
          >
            Cancel
          </button>
        </div>
      )}

      {/* URL Ingestion Trigger */}
      <div style={{ textAlign: "right" }}>
        <button
          onClick={() => setShowUrlForm(!showUrlForm)}
          style={{
            background: "transparent",
            border: "none",
            fontSize: "11px",
            color: "var(--text-secondary)",
            cursor: "pointer",
            padding: "4px 8px",
            textDecoration: "underline"
          }}
        >
          {showUrlForm ? "Hide URL Crawl" : "🌐 Crawl Web Page URL..."}
        </button>
      </div>

      {/* Inline URL Form */}
      {showUrlForm && (
        <form 
          onSubmit={handleUrlSubmit} 
          style={{ 
            padding: "12px", 
            background: "var(--surface-muted)", 
            border: "1px dashed var(--border)", 
            borderRadius: "var(--radius-md)",
            display: "flex", 
            flexDirection: "column", 
            gap: "8px",
            marginTop: "4px"
          }}
        >
          <label htmlFor="url-input-library" style={{ fontSize: "10px", fontWeight: "700", textTransform: "uppercase", color: "var(--text-secondary)" }}>
            URL Source Ingestion
          </label>
          <div style={{ display: "flex", gap: "8px" }}>
            <input
              id="url-input-library"
              type="url"
              placeholder="https://example.com/docs"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              style={{ 
                flex: 1, 
                height: "32px", 
                fontSize: "12px", 
                background: "var(--background)",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-xs)",
                padding: "0 8px",
                color: "var(--text-primary)"
              }}
              required
            />
            <button 
              className="button button-primary" 
              type="submit" 
              disabled={!url}
              style={{ 
                height: "32px", 
                padding: "0 12px", 
                fontSize: "11px", 
                borderRadius: "var(--radius-xs)",
                background: "var(--accent)",
                color: "white",
                border: "none",
                cursor: "pointer"
              }}
            >
              Fetch
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default UploadForm;
