import { useEffect, useState, useCallback } from "react";
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
    if (!file || !selectedCollectionId) return;
    setUploading(true);
    try {
      await uploadFile({ file, collectionId: selectedCollectionId });
      const docs = await listDocuments({ collectionId: selectedCollectionId });
      selectCollection(selectedCollectionId, collectionName, docs);
      
      // Also refresh the collections list to update counts
      const cols = await listCollections();
      setCollections(cols);
    } catch (err) {
      console.error("Upload failed:", err);
      alert("Failed to upload: " + err.message);
    } finally {
      setUploading(false);
    }
    e.target.value = "";
  }, [selectedCollectionId, collectionName, selectCollection]);

  const getCollectionIcon = (name) => {
    const lower = name.toLowerCase();
    if (lower.includes("marketing")) return "📢";
    if (lower.includes("tech") || lower.includes("code") || lower.includes("developer")) return "💻";
    if (lower.includes("design") || lower.includes("ui") || lower.includes("ux")) return "🎨";
    if (lower.includes("strategy") || lower.includes("product") || lower.includes("research")) return "🎯";
    return "📁";
  };

  return (
    <div className="sources-panel" style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <div 
        className="sources-header" 
        style={{ 
          padding: "16px 20px", 
          display: "flex", 
          flexDirection: "column", 
          gap: "4px", 
          borderBottom: "1px solid var(--border)" 
        }}
      >
        <span 
          style={{ 
            fontSize: "12px", 
            fontWeight: "800", 
            textTransform: "uppercase", 
            letterSpacing: "0.10em", 
            color: "var(--accent)" 
          }}
        >
          Workspace Sources
        </span>
      </div>

      {!selectedCollectionId ? (
        /* LIST OF ALL COLLECTIONS */
        <div style={{ flex: 1, overflowY: "auto", padding: "16px 12px" }}>
          {loading ? (
            <div style={{ padding: "32px", textAlign: "center" }}>
              <span className="spinner" style={{ display: "inline-block", width: "24px", height: "24px" }} />
            </div>
          ) : collections.length === 0 ? (
            <p style={{ fontSize: "12px", color: "var(--text-muted)", padding: "8px 12px", fontStyle: "italic" }}>
              No collections found. Create one in the Collections tab.
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              {collections.map((col) => (
                <div
                  key={col.id}
                  onClick={() => handleCollectionSelect(col)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "10px 12px",
                    borderRadius: "var(--radius-md)",
                    cursor: "pointer",
                    fontSize: "13px",
                    fontWeight: "600",
                    color: "var(--text-secondary)",
                    transition: "all var(--motion-base) var(--ease-standard)",
                  }}
                  className="sources-collection-header-row"
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", minWidth: 0 }}>
                    <span style={{ fontSize: "18px" }}>{getCollectionIcon(col.name)}</span>
                    <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {col.name}
                    </span>
                  </div>
                  <span 
                    style={{ 
                      height: "18px", 
                      minWidth: "18px", 
                      padding: "0 5px", 
                      fontSize: "10px", 
                      fontWeight: "700",
                      borderRadius: "10px", 
                      background: "var(--border)", 
                      color: "var(--text-secondary)",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center"
                    }}
                  >
                    {col.document_count}
                  </span>
                </div>
              ))}
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
              style={{ height: "30px", padding: "0 10px", fontSize: "12px", borderRadius: "var(--radius-sm)" }}
              onClick={() => selectCollection(null, null, [])}
            >
              ← Back
            </button>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", flex: 1 }}>
              <label 
                className="button button-primary" 
                style={{ 
                  height: "30px", 
                  padding: "0 10px", 
                  fontSize: "12px", 
                  cursor: uploading ? "not-allowed" : "pointer",
                  marginLeft: "auto",
                  borderRadius: "var(--radius-sm)"
                }}
              >
                <input
                  type="file"
                  onChange={handleUpload}
                  style={{ display: "none" }}
                  accept=".pdf,.txt,.md"
                  disabled={uploading}
                />
                {uploading ? "..." : "+ Add"}
              </label>
            </div>
          </div>

          <div style={{ flex: 1, overflowY: "auto", padding: "16px 12px" }}>
            <div className="sources-scope" style={{ marginBottom: "16px", padding: "0 8px" }}>
              <div style={{ fontSize: "14px", fontWeight: "750", color: "var(--text-primary)" }}>{collectionName}</div>
              <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
                {selectedDocumentIds.length} of {documents.length} selected
              </div>
            </div>

            {loading ? (
              <div style={{ padding: "32px", textAlign: "center" }}>
                <span className="spinner" style={{ display: "inline-block", width: "24px", height: "24px" }} />
              </div>
            ) : activeDocumentId ? (
              <SourceBrowser documentId={activeDocumentId} onClose={() => setActiveDocument(null)} inline />
            ) : documents.length === 0 ? (
              <p style={{ fontSize: "12px", color: "var(--text-muted)", padding: "16px", textAlign: "center", fontStyle: "italic" }}>
                No documents in this collection.
              </p>
            ) : (
              <div className="sources-doc-list" style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
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
                        style={{ width: "14px", height: "14px", cursor: "pointer" }}
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
                        width: "24px", 
                        height: "24px", 
                        padding: 0, 
                        minWidth: "24px", 
                        display: "flex", 
                        alignItems: "center", 
                        justifyContent: "center",
                        fontSize: "11px",
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
    </div>
  );
}
