import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useWorkspace } from "../../context/WorkspaceContext";

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
  const navigate = useNavigate();
  const { selectCollection } = useWorkspace();
  const [collections, setCollections] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

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

  const filteredCollections = useMemo(() => {
    return collections.filter((c) =>
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.description || "").toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [collections, searchQuery]);

  async function handleCreate(payload) {
    await createCollection(payload);
    await refreshData();
  }

  async function handleRename(collection, nextName) {
    if (!nextName || nextName === collection.name) {
      return;
    }
    await updateCollection(collection.id, { name: nextName });
    await refreshData();
  }

  async function handleDelete(collectionId) {
    if (!window.confirm("Are you sure you want to delete this collection?")) return;
    await deleteCollection(collectionId);
    await refreshData();
  }

  async function handleMoveDocument(documentId, collectionIds) {
    await moveDocument(documentId, collectionIds);
    await refreshData();
  }

  async function handleStartChat(collection) {
    const docs = documentsByCollection[collection.id] || [];
    selectCollection(collection.id, collection.name, docs);
    navigate("/chat");
  }

  return (
    <div className="page-shell">
      {/* Top Header Row with "+ New Collection" action */}
      <div 
        className="dashboard-header" 
        style={{ 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "center", 
          marginBottom: "32px",
          flexWrap: "wrap",
          gap: "16px"
        }}
      >
        <div>
          <span className="eyebrow">Knowledge Architecture</span>
          <h1 style={{ fontSize: "24px", fontWeight: "750", letterSpacing: "-0.03em", margin: "4px 0 8px 0" }}>
            COLLECTIONS OVERVIEW
          </h1>
          <p style={{ margin: 0, color: "var(--text-secondary)" }}>
            Organize files into collections to focus retrieval boundaries during conversational reasoning.
          </p>
        </div>
        <button 
          className="button button-primary" 
          onClick={() => setIsModalOpen(true)}
          style={{ 
            height: "40px", 
            padding: "0 20px", 
            background: "var(--accent)", 
            color: "white",
            border: "none",
            borderRadius: "var(--radius-md)",
            fontWeight: "600",
            cursor: "pointer"
          }}
        >
          + New Collection
        </button>
      </div>

      {error ? (
        <section className="error-banner" style={{ marginBottom: "24px" }}>
          <strong>Request failed:</strong> {error}
        </section>
      ) : null}

      {/* Search and Metadata Filter Row */}
      <div 
        style={{ 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "center", 
          marginBottom: "24px", 
          flexWrap: "wrap", 
          gap: "16px" 
        }}
      >
        <div style={{ position: "relative", width: "100%", maxWidth: "340px" }}>
          <input 
            type="text" 
            placeholder="Search collections..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 16px 10px 38px",
              background: "var(--surface-muted)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-pill)",
              fontSize: "13px",
              color: "var(--text-primary)"
            }}
          />
          <span style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", fontSize: "14px", opacity: 0.6 }}>🔍</span>
        </div>
        <div style={{ fontSize: "12px", color: "var(--text-secondary)", fontWeight: "600" }}>
          {filteredCollections.length} of {collections.length} Collections Total
        </div>
      </div>

      {/* Grid of collections folder cards */}
      <section className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "24px" }}>
        {filteredCollections.length ? (
          filteredCollections.map((collection) => (
            <CollectionCard
              key={collection.id}
              allCollections={collections}
              collection={collection}
              documents={documentsByCollection[collection.id] || []}
              onDelete={handleDelete}
              onMoveDocument={handleMoveDocument}
              onRename={handleRename}
              onStartChat={handleStartChat}
            />
          ))
        ) : (
          <section className="panel glassmorphic" style={{ gridColumn: "1 / -1", padding: "40px", textAlign: "center" }}>
            <div className="empty-state">
              <h3 style={{ fontSize: "16px", marginBottom: "8px", fontWeight: "750" }}>
                {searchQuery ? "No matches found" : "No collections yet"}
              </h3>
              <p style={{ color: "var(--text-secondary)", fontSize: "13px", margin: 0 }}>
                {searchQuery 
                  ? "Try adjusting your search terms to locate your collection." 
                  : "Create your first collection to start organizing ingested documents."
                }
              </p>
            </div>
          </section>
        )}
      </section>

      {/* Modal overlay form */}
      {isModalOpen && (
        <div 
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: "100vw",
            height: "100vh",
            background: "rgba(0, 0, 0, 0.65)",
            backdropFilter: "blur(6px)",
            WebkitBackdropFilter: "blur(6px)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000
          }} 
          onClick={() => setIsModalOpen(false)}
        >
          <div 
            style={{ 
              background: "var(--surface)", 
              border: "1px solid var(--border)", 
              borderRadius: "var(--radius-lg)", 
              padding: "24px", 
              width: "90%", 
              maxWidth: "480px",
              boxShadow: "var(--shadow-lg)"
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <CollectionForm 
              onSubmit={async (payload) => {
                await handleCreate(payload);
                setIsModalOpen(false);
              }}
              onCancel={() => setIsModalOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default CollectionsScreen;
