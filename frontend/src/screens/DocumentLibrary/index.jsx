import { useEffect, useState } from "react";

import {
  decideDuplicate,
  deleteDocument,
  getIngestionAttempt,
  listCollections,
  listDocuments,
  listIngestionAttempts,
  moveDocument,
  reingestDocument,
  submitUrl,
  uploadFile,
} from "../../api/knowledgeApi";
import DocumentTable from "../../components/DocumentTable";
import UploadForm from "../../components/UploadForm";
import DuplicateDecisionScreen from "../DuplicateDecision";

function DocumentLibraryScreen() {
  const [collections, setCollections] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [pendingAttempts, setPendingAttempts] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState("");
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function refreshData() {
    setLoading(true);
    try {
      const [collectionsPayload, documentsPayload, attemptsPayload] = await Promise.all([
        listCollections(),
        listDocuments({ collectionId: selectedCollection, query }),
        listIngestionAttempts("awaiting_user_action"),
      ]);
      setCollections(collectionsPayload);
      setDocuments(documentsPayload);
      setPendingAttempts(attemptsPayload);
      setError("");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshData();
  }, [selectedCollection, query]);

  async function handleUploadFile(payload) {
    setError("");
    const attempt = await uploadFile(payload);
    const refreshed = await getIngestionAttempt(attempt.id);
    if (refreshed.status === "awaiting_user_action") {
      setPendingAttempts((current) => [refreshed, ...current]);
    }
    await refreshData();
  }

  async function handleSubmitUrl(payload) {
    setError("");
    const attempt = await submitUrl(payload);
    const refreshed = await getIngestionAttempt(attempt.id);
    if (refreshed.status === "awaiting_user_action") {
      setPendingAttempts((current) => [refreshed, ...current]);
    }
    await refreshData();
  }

  async function handleDuplicateDecision(attemptId, action) {
    await decideDuplicate(attemptId, action);
    await refreshData();
  }

  async function handleDelete(documentId) {
    await deleteDocument(documentId);
    await refreshData();
  }

  async function handleMove(document, collectionIds) {
    await moveDocument(document.id, collectionIds);
    await refreshData();
  }

  async function handleReingest(document) {
    await reingestDocument(
      document.id,
      document.collections.map((collection) => collection.id),
    );
    await refreshData();
  }

  return (
    <div className="page-shell">
      <div className="hero">
        <div className="hero-header">
          <div>
            <span className="eyebrow">Document Intelligence</span>
            <h1>Knowledge Library</h1>
            <p className="hero-copy">Upload, manage, and inspect your source documents. Keep your knowledge base clean and context-ready.</p>
          </div>
        </div>
      </div>

      {error ? (
        <section className="error-banner">
          <strong>Request failed:</strong> {error}
        </section>
      ) : null}

      <UploadForm
        collections={collections}
        onUploadFile={handleUploadFile}
        onSubmitUrl={handleSubmitUrl}
      />

      <section className="panel" style={{ border: "1px solid var(--border-strong)" }}>
        <div className="panel-heading">
          <div>
            <h3>Inventory Filters</h3>
            <p>Narrow your view by collection or search for specific document titles.</p>
          </div>
        </div>
        <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "24px" }}>
          <div className="field">
            <label htmlFor="collection-filter">Scope by Collection</label>
            <select
              id="collection-filter"
              value={selectedCollection}
              onChange={(event) => setSelectedCollection(event.target.value)}
            >
              <option value="">All indexed collections</option>
              {collections.map((collection) => (
                <option key={collection.id} value={collection.id}>
                  {collection.name}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="search-input">Semantic Search</label>
            <input
              id="search-input"
              placeholder="Filter by title or metadata..."
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </div>
        </div>
      </section>

      <DuplicateDecisionScreen attempts={pendingAttempts} onDecide={handleDuplicateDecision} />

      {loading ? (
        <div className="empty-state">
          <div className="spinner" style={{ marginBottom: "20px" }}></div>
          <p className="mono" style={{ fontSize: "14px" }}>Synchronizing inventory...</p>
        </div>
      ) : (
        <DocumentTable
          collections={collections}
          documents={documents}
          onDelete={handleDelete}
          onMove={handleMove}
          onReingest={handleReingest}
        />
      )}
    </div>
  );
}

export default DocumentLibraryScreen;
