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
    <div className="stack">
      {error ? (
        <section className="panel panel-danger">
          <h2>Request failed</h2>
          <p>{error}</p>
        </section>
      ) : null}
      <UploadForm
        collections={collections}
        onUploadFile={handleUploadFile}
        onSubmitUrl={handleSubmitUrl}
      />
      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Filters</h2>
            <p>Search by title or filename and narrow results to a collection.</p>
          </div>
        </div>
        <div className="filter-row">
          <label className="field">
            <span>Collection filter</span>
            <select
              value={selectedCollection}
              onChange={(event) => setSelectedCollection(event.target.value)}
            >
              <option value="">All collections</option>
              {collections.map((collection) => (
                <option key={collection.id} value={collection.id}>
                  {collection.name}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Search</span>
            <input
              placeholder="Search by title or filename"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
        </div>
      </section>
      <DuplicateDecisionScreen attempts={pendingAttempts} onDecide={handleDuplicateDecision} />
      {loading ? (
        <section className="panel">
          <p>Loading document inventory…</p>
        </section>
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
