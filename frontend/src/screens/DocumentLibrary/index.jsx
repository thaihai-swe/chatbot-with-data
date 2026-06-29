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
import SourceBrowser from "../../components/SourceBrowser";
import UploadForm from "../../components/UploadForm";
import DuplicateDecisionScreen from "../DuplicateDecision";

function DocumentLibraryScreen() {
  const [collections, setCollections] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [pendingAttempts, setPendingAttempts] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState("");
  const [query, setQuery] = useState("");
  const [activeDocumentId, setActiveDocumentId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function refreshData(showSpinner = true) {
    if (showSpinner) {
      setLoading(true);
    }
    try {
      const [collectionsPayload, documentsPayload, attemptsPayload] = await Promise.all([
        listCollections(),
        listDocuments({ collectionId: selectedCollection, query }),
        listIngestionAttempts(),
      ]);
      setCollections(collectionsPayload);

      const awaitingUserAction = [];
      const tableAttempts = [];

      for (const attempt of attemptsPayload) {
        if (attempt.status === "awaiting_user_action") {
          awaitingUserAction.push(attempt);
        } else if (
          attempt.status === "submitted" ||
          attempt.status === "processing" ||
          attempt.status === "failed"
        ) {
          // If collection filter is active, only show attempts for this collection
          if (selectedCollection && !(attempt.collection_ids || []).includes(selectedCollection)) {
            continue;
          }

          // If search query is active, filter attempts by query
          if (query) {
            const lowerQuery = query.toLowerCase();
            const titleMatch = (attempt.title || "").toLowerCase().includes(lowerQuery);
            const fileMatch = (attempt.submitted_filename || "").toLowerCase().includes(lowerQuery);
            const uriMatch = (attempt.source_uri || "").toLowerCase().includes(lowerQuery);
            if (!titleMatch && !fileMatch && !uriMatch) {
              continue;
            }
          }

          // Check if this attempt is already associated with a completed document in documentsPayload
          const isDocInPayload = documentsPayload.some((d) => d.id === attempt.document_id);
          if (!isDocInPayload) {
            tableAttempts.push(attempt);
          }
        }
      }

      const formattedAttempts = tableAttempts.map((attempt) => {
        const attemptCollections = (attempt.collection_ids || [])
          .map((cid) => {
            const col = collectionsPayload.find((c) => c.id === cid);
            return col ? { id: col.id, name: col.name } : null;
          })
          .filter(Boolean);

        return {
          id: attempt.id,
          title: attempt.title || attempt.submitted_filename || attempt.source_uri || "Untitled",
          source_type: attempt.source_type,
          collections: attemptCollections,
          latest_status: attempt.status,
          is_attempt: true,
          created_at: attempt.created_at,
        };
      });

      const allItems = [
        ...formattedAttempts,
        ...documentsPayload.map((d) => ({ ...d, is_attempt: false })),
      ];

      allItems.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

      setDocuments(allItems);
      setPendingAttempts(awaitingUserAction);
      setError("");
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      if (showSpinner) {
        setLoading(false);
      }
    }
  }

  useEffect(() => {
    refreshData(true);
  }, [selectedCollection, query]);

  useEffect(() => {
    const hasActiveAttempts = documents.some(
      (doc) =>
        doc.is_attempt &&
        (doc.latest_status === "submitted" || doc.latest_status === "processing"),
    );

    if (hasActiveAttempts) {
      const interval = setInterval(() => {
        refreshData(false);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [documents]);

  async function handleUploadFile(payload) {
    setError("");
    try {
      await uploadFile(payload);
      await refreshData(false);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleSubmitUrl(payload) {
    setError("");
    try {
      await submitUrl(payload);
      await refreshData(false);
    } catch (err) {
      setError(err.message);
    }
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
      <div className="dashboard-header">
        <div>
          <span className="eyebrow">Document Intelligence</span>
          <h1>Knowledge Library</h1>
          <p>Upload, manage, and inspect your source documents. Keep your knowledge base clean and context-ready.</p>
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

      <div className="filter-row">
        <div className="field">
          <label htmlFor="collection-filter" className="sr-only" style={{ display: "none" }}>Scope by Collection</label>
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
          <label htmlFor="search-input" className="sr-only" style={{ display: "none" }}>Semantic Search</label>
          <input
            id="search-input"
            placeholder="Filter by title or metadata..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
      </div>

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
          onViewDocument={(id) => setActiveDocumentId(id)}
        />
      )}

      {activeDocumentId && (
        <SourceBrowser
          documentId={activeDocumentId}
          onClose={() => setActiveDocumentId(null)}
        />
      )}
    </div>
  );
}

export default DocumentLibraryScreen;
