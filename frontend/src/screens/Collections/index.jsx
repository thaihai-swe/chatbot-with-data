import { useEffect, useMemo, useState } from "react";

import {
  createCollection,
  deleteCollection,
  listCollections,
  listDocuments,
  moveDocument,
  updateCollection,
} from "../../api/knowledgeApi";
import CollectionCard from "../../components/CollectionCard";
import CollectionForm from "../../components/CollectionForm";

function CollectionsScreen() {
  const [collections, setCollections] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState("");

  async function refreshData() {
    try {
      const [collectionsPayload, documentsPayload] = await Promise.all([
        listCollections(),
        listDocuments(),
      ]);
      setCollections(collectionsPayload);
      setDocuments(documentsPayload);
      setError("");
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  useEffect(() => {
    refreshData();
  }, []);

  const documentsByCollection = useMemo(() => {
    const mapping = {};
    collections.forEach((collection) => {
      mapping[collection.id] = documents.filter((document) =>
        document.collections.some((membership) => membership.id === collection.id),
      );
    });
    return mapping;
  }, [collections, documents]);

  async function handleCreate(payload) {
    await createCollection(payload);
    await refreshData();
  }

  async function handleRename(collection) {
    const nextName = window.prompt("Rename collection", collection.name);
    if (!nextName || nextName === collection.name) {
      return;
    }
    await updateCollection(collection.id, { name: nextName });
    await refreshData();
  }

  async function handleDelete(collectionId) {
    await deleteCollection(collectionId);
    await refreshData();
  }

  async function handleMoveDocument(documentId, collectionIds) {
    await moveDocument(documentId, collectionIds);
    await refreshData();
  }

  return (
    <div className="page-shell">
      <div className="hero">
        <div>
          <span className="eyebrow">Knowledge Architecture</span>
          <h1>Document Collections</h1>
          <p className="hero-copy">Organize your document library into logical groups for targeted retrieval and context management.</p>
        </div>
      </div>

      {error ? (
        <section className="error-banner">
          <strong>Request failed:</strong> {error}
        </section>
      ) : null}

      <CollectionForm onSubmit={handleCreate} />
      
      <section className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))" }}>
        {collections.length ? (
          collections.map((collection) => (
            <CollectionCard
              key={collection.id}
              allCollections={collections}
              collection={collection}
              documents={documentsByCollection[collection.id] || []}
              onDelete={handleDelete}
              onMoveDocument={handleMoveDocument}
              onRename={handleRename}
            />
          ))
        ) : (
          <section className="panel" style={{ gridColumn: "1 / -1" }}>
            <div className="empty-state">
              <h3 style={{ fontSize: "20px", marginBottom: "12px" }}>No collections yet</h3>
              <p style={{ color: "var(--text-secondary)", fontSize: "15px" }}>Create your first collection to start organizing ingested documents.</p>
            </div>
          </section>
        )}
      </section>
    </div>
  );
}

export default CollectionsScreen;
