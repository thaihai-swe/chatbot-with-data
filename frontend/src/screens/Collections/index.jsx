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
    <div className="stack">
      {error ? (
        <section className="panel panel-danger">
          <h2>Request failed</h2>
          <p>{error}</p>
        </section>
      ) : null}
      <CollectionForm onSubmit={handleCreate} />
      <section className="grid">
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
          <section className="panel">
            <h2>No collections yet</h2>
            <p>Create a collection to start organizing ingested documents.</p>
          </section>
        )}
      </section>
    </div>
  );
}

export default CollectionsScreen;
