import { useEffect, useState, useMemo } from "react";

import {
  createCollection,
  decideDuplicate,
  deleteDocument,
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
import CollectionForm from "../../components/CollectionForm";

function DocumentLibraryScreen() {
  const [collections, setCollections] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [pendingAttempts, setPendingAttempts] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState("");
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [collectionSearch, setCollectionSearch] = useState("");

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

  async function handleCreate(payload) {
    setError("");
    try {
      await createCollection(payload);
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

  // Filter documents list based on Selected Status Tab
  const filteredDocuments = documents.filter((doc) => {
    if (statusFilter === "all") return true;
    if (statusFilter === "pending") return doc.is_attempt && doc.latest_status === "submitted";
    if (statusFilter === "processing") return doc.is_attempt && doc.latest_status === "processing";
    if (statusFilter === "completed") return !doc.is_attempt;
    return true;
  });

  const filteredCollectionsForTree = useMemo(() => {
    return collections.filter((col) =>
      col.name.toLowerCase().includes(collectionSearch.toLowerCase())
    );
  }, [collections, collectionSearch]);

  return (
    <div className="page-shell">
      {error ? (
        <section className="error-banner" style={{ marginBottom: "24px" }}>
          <strong>Request failed:</strong> {error}
        </section>
      ) : null}

      <DuplicateDecisionScreen attempts={pendingAttempts} onDecide={handleDuplicateDecision} />

      {/* Grid Layout: Left (Source Browser Sidebar), Right (Document Workspace) */}
      <div style={{ display: "grid", gridTemplateColumns: "240px 1fr", gap: "24px", alignItems: "start", minHeight: "calc(100vh - 120px)" }}>
        
        {/* Left Column: SOURCE BROWSER */}
        <div 
          className="panel glassmorphic" 
          style={{ 
            padding: "16px", 
            display: "flex", 
            flexDirection: "column", 
            gap: "16px",
            borderRadius: "var(--radius-lg)",
            border: "1px solid var(--border)",
            height: "100%",
            minHeight: "450px"
          }}
        >
          <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
            <span className="eyebrow" style={{ fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.08em" }}>
              Workspace Inventory
            </span>
            <h3 style={{ fontSize: "14px", fontWeight: "750", margin: 0, color: "var(--text-primary)" }}>
              SOURCE BROWSER
            </h3>
          </div>

          {/* Collection Name Search Box */}
          <div style={{ position: "relative", width: "100%" }}>
            <input 
              type="text" 
              placeholder="Search collections..." 
              value={collectionSearch}
              onChange={(e) => setCollectionSearch(e.target.value)}
              style={{
                width: "100%",
                padding: "8px 12px 8px 30px",
                background: "var(--surface-muted)",
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-sm)",
                fontSize: "12px",
                color: "var(--text-primary)",
                outline: "none"
              }}
            />
            <span style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", fontSize: "12px", opacity: 0.5 }}>🔍</span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            {/* Global All Documents selection */}
            <div 
              onClick={() => setSelectedCollection("")}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "8px 12px",
                cursor: "pointer",
                borderRadius: "var(--radius-md)",
                background: selectedCollection === "" ? "rgba(255, 255, 255, 0.04)" : "transparent",
                color: selectedCollection === "" ? "var(--text-primary)" : "var(--text-secondary)",
                fontWeight: selectedCollection === "" ? "700" : "500",
                fontSize: "12.5px",
                transition: "all var(--motion-fast) var(--ease-standard)",
                marginBottom: "4px"
              }}
              className="sources-collection-header-row"
            >
              <span>📂</span>
              <span>All Documents</span>
            </div>

            {/* Collections directory list (without nesting) */}
            <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
              {filteredCollectionsForTree.map((col) => {
                const isActive = selectedCollection === col.id;
                return (
                  <div 
                    key={col.id}
                    onClick={() => setSelectedCollection(col.id)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      padding: "6px 10px",
                      cursor: "pointer",
                      borderRadius: "var(--radius-sm)",
                      background: isActive ? "rgba(255, 255, 255, 0.04)" : "transparent",
                      color: isActive ? "var(--text-primary)" : "var(--text-secondary)",
                      fontWeight: isActive ? "700" : "500",
                      fontSize: "12.5px",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      transition: "all var(--motion-fast) var(--ease-standard)"
                    }}
                    className="sources-collection-header-row"
                    title={col.name}
                  >
                    <span>📁</span>
                    <span>{col.name}</span>
                  </div>
                );
              })}
              {filteredCollectionsForTree.length === 0 && (
                <span style={{ fontSize: "11px", color: "var(--text-muted)", fontStyle: "italic", padding: "8px 10px" }}>
                  No collections matched
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: DOCUMENT WORKSPACE */}
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          
          {/* Top Row: Search (left) & Upload (right) */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: "20px", alignItems: "center" }}>
            {/* Search Input Bar */}
            <div style={{ position: "relative", width: "100%" }}>
              <input 
                type="text" 
                placeholder="Search all documents, tags, or metadata..." 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                style={{
                  width: "100%",
                  height: "44px",
                  padding: "10px 16px 10px 42px",
                  background: "var(--surface)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-md)",
                  fontSize: "13.5px",
                  color: "var(--text-primary)"
                }}
              />
              <span style={{ position: "absolute", left: "16px", top: "50%", transform: "translateY(-50%)", fontSize: "16px", opacity: 0.6 }}>🔍</span>
            </div>

            {/* Ingestion Upload component */}
            <UploadForm
              activeCollectionId={selectedCollection}
              onUploadFile={handleUploadFile}
              onSubmitUrl={handleSubmitUrl}
            />
          </div>

          {/* Sub-Header Row: Section details and quick actions */}
          <div 
            style={{ 
              display: "flex", 
              justifyContent: "space-between", 
              alignItems: "center",
              borderTop: "1px solid var(--border)",
              paddingTop: "20px",
              marginTop: "4px"
            }}
          >
            <div>
              <h2 style={{ fontSize: "16px", fontWeight: "750", margin: 0, color: "var(--text-primary)" }}>
                Ingested Documents
                <span style={{ color: "var(--text-muted)", fontSize: "12px", fontWeight: "500", marginLeft: "8px" }}>
                  ({filteredDocuments.length} files)
                </span>
              </h2>
            </div>
            
            <div style={{ display: "flex", gap: "8px" }}>
              <button 
                className="button button-secondary"
                onClick={() => setIsModalOpen(true)}
                style={{ 
                  height: "36px", 
                  padding: "0 16px", 
                  fontSize: "12px", 
                  border: "1px solid var(--border-strong)",
                  borderRadius: "var(--radius-md)",
                  fontWeight: "600"
                }}
              >
                + Add New Folder
              </button>
              <button 
                className="button button-ghost"
                onClick={() => refreshData(true)}
                style={{ 
                  height: "36px", 
                  padding: "0 12px", 
                  fontSize: "12px", 
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-md)"
                }}
              >
                🔄 Refresh
              </button>
            </div>
          </div>

          {/* Status Tab buttons */}
          <div style={{ display: "flex", gap: "6px" }}>
            {[
              { id: "all", label: "All Sources" },
              { id: "pending", label: "Pending" },
              { id: "processing", label: "Processing" },
              { id: "completed", label: "Completed" }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                className={`button ${statusFilter === tab.id ? 'button-primary' : 'button-ghost'}`}
                style={{ height: "30px", padding: "0 14px", fontSize: "11px", borderRadius: "var(--radius-sm)" }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Table display */}
          {loading ? (
            <div className="panel glassmorphic" style={{ padding: "80px 40px", textAlign: "center", borderRadius: "var(--radius-lg)" }}>
              <div className="spinner" style={{ margin: "0 auto 20px auto" }}></div>
              <p className="mono" style={{ fontSize: "13px", color: "var(--text-secondary)", margin: 0 }}>
                Synchronizing document inventory...
              </p>
            </div>
          ) : (
            <DocumentTable
              collections={collections}
              documents={filteredDocuments}
              onDelete={handleDelete}
              onMove={handleMove}
              onReingest={handleReingest}
              onViewDocument={(id) => setActiveDocumentId(id)}
            />
          )}
        </div>

      </div>

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
