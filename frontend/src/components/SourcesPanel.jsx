import { useEffect, useState, useCallback, useMemo } from "react";
import { useWorkspace } from "../context/WorkspaceContext";
import { listCollections, listDocuments, uploadFile } from "../api/knowledgeApi";
import SourceBrowser from "./SourceBrowser";

export default function SourcesPanel() {
  const {
    selectedCollectionId,
    collectionName,
    selectedDocumentIds,
    documents,
    activeDocumentId,
    selectCollection,
    toggleDocument,
    setActiveDocument,
  } = useWorkspace();

  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    setLoading(true);
    listCollections()
      .then(setCollections)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleCollectionSelect = useCallback(async (col) => {
    setLoading(true);
    try {
      const docs = await listDocuments({ collectionId: col.id });
      selectCollection(col.id, col.name, docs);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setLoading(false);
    }
  }, [selectCollection]);

  const handleUpload = useCallback(async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    let targetCollectionId = selectedCollectionId;
    
    // If no collection is active, use the first available collection, or warn the user.
    if (!targetCollectionId) {
      if (collections.length > 0) {
        targetCollectionId = collections[0].id;
      } else {
        alert("Please select a collection folder first to upload files.");
        return;
      }
    }

    setUploading(false);
    try {
      await uploadFile({ file, collectionId: targetCollectionId });
      const docs = await listDocuments({ collectionId: targetCollectionId });
      selectCollection(targetCollectionId, collectionName || collections[0].name, docs);
      
      const cols = await listCollections();
      setCollections(cols);
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Failed to upload: " + err.message);
    }
    e.target.value = "";
  }, [selectedCollectionId, collectionName, collections, selectCollection]);

  const getCollectionIcon = (name) => {
    const lower = name.toLowerCase();
    if (lower.includes("financial") || lower.includes("revenue") || lower.includes("report")) return "📈";
    if (lower.includes("feedback") || lower.includes("customer")) return "💬";
    if (lower.includes("manual") || lower.includes("product")) return "📘";
    if (lower.includes("agreement") || lower.includes("legal")) return "📜";
    return "📁";
  };

  const getCollectionStatusColor = (col, idx) => {
    // Return status dot colors based on mockup guidelines
    if (col.document_count === 0) return "#eab308"; // Inactive 🟡
    if (idx % 3 === 1) return "#3b82f6"; // Processing 🔵
    return "#00d992"; // Active 🟢
  };

  const filteredCollections = useMemo(() => {
    return collections.filter(col =>
      col.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [collections, searchQuery]);

  const accentColor = "#00d992"; // Electric green from mockup

  return (
    <div className="sources-panel" style={{ height: "100%", display: "flex", flexDirection: "column", background: "var(--surface)" }}>
      {/* Sidebar Top Search & Upload Panel */}
      <div 
        className="sources-header" 
        style={{ 
          padding: "16px 16px 12px 16px", 
          display: "flex", 
          flexDirection: "column", 
          gap: "12px", 
          borderBottom: "1px solid var(--border)" 
        }}
      >
        <span 
          style={{ 
            fontSize: "10px", 
            fontWeight: "800", 
            textTransform: "uppercase", 
            letterSpacing: "0.10em", 
            color: "var(--text-muted)",
            display: "block"
          }}
        >
          Documents
        </span>

        {/* 1. Search Box */}
        <div style={{ position: "relative", width: "100%" }}>
          <input 
            type="text" 
            placeholder="Search sources..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              height: "36px",
              padding: "0 10px 0 32px",
              background: "var(--background)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-md)",
              fontSize: "12.5px",
              color: "var(--text-primary)"
            }}
          />
          <span style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", fontSize: "13px", opacity: 0.5 }}>🔍</span>
        </div>

        {/* 2. + Upload Files button */}
        <label 
          className="button button-primary" 
          style={{ 
            height: "36px", 
            width: "100%",
            padding: 0, 
            fontSize: "12.5px", 
            cursor: uploading ? "not-allowed" : "pointer",
            borderRadius: "var(--radius-md)",
            background: accentColor,
            color: "black",
            fontWeight: "750",
            border: "none",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "6px"
          }}
        >
          <input
            type="file"
            onChange={handleUpload}
            style={{ display: "none" }}
            accept=".pdf,.txt,.md,.markdown,.docx,.doc,.csv,.xlsx,.xls"
            disabled={uploading}
          />
          <span>{uploading ? "Uploading..." : "+ Upload Files"}</span>
        </label>
      </div>

      {!selectedCollectionId ? (
        /* LIST OF ALL COLLECTIONS */
        <div style={{ flex: 1, overflowY: "auto", padding: "12px 8px" }}>
          {loading ? (
            <div style={{ padding: "32px", textAlign: "center" }}>
              <span className="spinner" style={{ display: "inline-block", width: "24px", height: "24px" }} />
            </div>
          ) : filteredCollections.length === 0 ? (
            <p style={{ fontSize: "11px", color: "var(--text-muted)", padding: "12px", fontStyle: "italic", textAlign: "center" }}>
              {searchQuery ? "No matches found" : "No collections found."}
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
              {filteredCollections.map((col, idx) => {
                const statusColor = getCollectionStatusColor(col, idx);
                const statusText = statusColor === "#00d992" ? "Active" : statusColor === "#3b82f6" ? "Processing" : "Inactive";
                
                return (
                  <div
                    key={col.id}
                    onClick={() => handleCollectionSelect(col)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "10px 12px",
                      borderRadius: "var(--radius-sm)",
                      cursor: "pointer",
                      fontSize: "12.5px",
                      fontWeight: "600",
                      color: "var(--text-secondary)",
                      transition: "all var(--motion-fast) var(--ease-standard)",
                    }}
                    className="sources-collection-header-row"
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "10px", minWidth: 0 }}>
                      <span style={{ fontSize: "16px" }}>{getCollectionIcon(col.name)}</span>
                      <div style={{ display: "flex", flexDirection: "column", minWidth: 0 }}>
                        <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", color: "var(--text-primary)" }}>
                          {col.name}
                        </span>
                        <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "4px", marginTop: "1px" }}>
                          <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: statusColor }} />
                          {statusText} • {col.document_count} files
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : (
        /* OPENED COLLECTION: SHOW ONLY ITS DOCUMENTS */
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          {/* Active Collection Header controls */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px", padding: "12px", borderBottom: "1px solid var(--border)" }}>
            <button 
              className="button button-ghost" 
              style={{ height: "28px", padding: "0 10px", fontSize: "11px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border)" }}
              onClick={() => selectCollection(null, null, [])}
            >
              ← Back
            </button>
            <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>Folders List</span>
          </div>

          <div style={{ flex: 1, overflowY: "auto", padding: "12px 8px" }}>
            <div className="sources-scope" style={{ marginBottom: "12px", padding: "0 8px" }}>
              <div style={{ fontSize: "13px", fontWeight: "750", color: "var(--text-primary)" }}>{collectionName}</div>
              <div style={{ fontSize: "10px", color: "var(--text-muted)", marginTop: "2px" }}>
                {selectedDocumentIds.length} of {documents.length} context elements selected
              </div>
            </div>

            {loading ? (
              <div style={{ padding: "32px", textAlign: "center" }}>
                <span className="spinner" style={{ display: "inline-block", width: "24px", height: "24px" }} />
              </div>
            ) : documents.length === 0 ? (
              <p style={{ fontSize: "11px", color: "var(--text-muted)", padding: "16px", textAlign: "center", fontStyle: "italic" }}>
                No documents in this folder.
              </p>
            ) : (
              <div className="sources-doc-list" style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                {documents.map((doc) => (
                  <div 
                    key={doc.id} 
                    className="sources-tree-doc-row" 
                    style={{ 
                      display: "flex", 
                      alignItems: "center", 
                      justifyContent: "space-between", 
                      padding: "6px 8px", 
                      borderRadius: "var(--radius-sm)" 
                    }}
                  >
                    <label style={{ display: "flex", alignItems: "center", gap: "8px", flex: 1, minWidth: 0, cursor: "pointer" }}>
                      <input
                        type="checkbox"
                        checked={selectedDocumentIds.includes(doc.id)}
                        onChange={() => toggleDocument(doc.id)}
                        style={{ width: "13px", height: "13px", cursor: "pointer", accentColor: accentColor }}
                      />
                      <span 
                        style={{ 
                          fontSize: "12px", 
                          fontWeight: "500", 
                          whiteSpace: "nowrap", 
                          overflow: "hidden", 
                          textOverflow: "ellipsis" 
                        }}
                      >
                        📄 {doc.title || "Untitled"}
                      </span>
                    </label>
                    <button
                      className="button button-ghost"
                      style={{ 
                        width: "20px", 
                        height: "20px", 
                        padding: 0, 
                        minWidth: "20px", 
                        display: "flex", 
                        alignItems: "center", 
                        justifyContent: "center",
                        fontSize: "10px",
                        borderRadius: "4px" 
                      }}
                      onClick={() => setActiveDocument(doc.id)}
                      title="Inspect document"
                    >
                      👁
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
      {activeDocumentId && (
        <SourceBrowser documentId={activeDocumentId} onClose={() => setActiveDocument(null)} />
      )}
    </div>
  );
}
