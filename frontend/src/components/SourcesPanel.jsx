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

  useEffect(() => {
    listCollections().then(setCollections).catch(console.error);
  }, []);

  const handleCollectionChange = useCallback(async (e) => {
    const id = e.target.value;
    if (!id) return;
    setLoading(true);
    try {
      const col = collections.find((c) => c.id === id);
      const docs = await listDocuments({ collectionId: id });
      selectCollection(id, col?.name || "Untitled", docs);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setLoading(false);
    }
  }, [collections, selectCollection]);

  const handleUpload = useCallback(async (e) => {
    const file = e.target.files?.[0];
    if (!file || !selectedCollectionId) return;
    try {
      await uploadFile({ file, collectionId: selectedCollectionId });
      const docs = await listDocuments({ collectionId: selectedCollectionId });
      selectCollection(selectedCollectionId, collectionName, docs);
    } catch (err) {
      console.error("Upload failed:", err);
    }
    e.target.value = "";
  }, [selectedCollectionId, collectionName, selectCollection]);

  return (
    <div className="sources-panel">
      <div className="sources-header">
        <select
          className="sources-collection-select"
          value={selectedCollectionId || ""}
          onChange={handleCollectionChange}
        >
          <option value="">Select collection...</option>
          {collections.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <label className="sources-upload-label" title="Upload file">
          <input
            type="file"
            onChange={handleUpload}
            style={{ display: "none" }}
            accept=".pdf,.txt,.md"
          />
          <span className="sources-upload-btn">+</span>
        </label>
      </div>

      {!selectedCollectionId ? (
        <div className="panel-empty-state" style={{ flex: 1, justifyContent: "flex-start", paddingTop: "32px" }}>
          <span style={{ fontSize: "24px", marginBottom: "8px" }}>📁</span>
          <p>Select a collection to begin</p>
        </div>
      ) : (
        <>
          <div className="sources-scope">
            {collectionName && (
              <span className="sources-scope-label">
                {collectionName} ({selectedDocumentIds.length}/{documents.length} documents)
              </span>
            )}
          </div>

          {loading ? (
            <div className="panel-empty-state">
              <div className="spinner" />
            </div>
          ) : activeDocumentId ? (
            <SourceBrowser documentId={activeDocumentId} onClose={() => setActiveDocument(null)} inline />
          ) : (
            <div className="sources-doc-list">
              {documents.map((doc) => (
                <div key={doc.id} className="sources-doc-item">
                  <label className="sources-doc-check">
                    <input
                      type="checkbox"
                      checked={selectedDocumentIds.includes(doc.id)}
                      onChange={() => toggleDocument(doc.id)}
                    />
                    <span className="sources-doc-title">{doc.title || "Untitled"}</span>
                  </label>
                  <button
                    className="sources-doc-view"
                    onClick={() => setActiveDocument(doc.id)}
                    title="View document"
                  >
                    👁
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
