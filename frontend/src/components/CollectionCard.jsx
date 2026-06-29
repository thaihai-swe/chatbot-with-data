import React, { useState } from "react";

function CollectionCard({
  collection,
  documents,
  allCollections,
  onRename,
  onDelete,
  onMoveDocument,
}) {
  const [generatingType, setGeneratingType] = useState(null);
  const [productResult, setProductResult] = useState(null);

  const handleGenerateProduct = async (type, label) => {
    setGeneratingType(type);
    setProductResult(null);
    const apiBase = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
    try {
      const response = await fetch(`${apiBase}/collections/${collection.id}/generate/${type}`, {
        method: "POST"
      });
      if (!response.ok) {
        throw new Error(`Failed to generate: ${response.statusText}`);
      }
      const data = await response.json();
      setProductResult({
        title: `${label} - ${collection.name}`,
        type,
        data
      });
    } catch (err) {
      alert(err.message);
    } finally {
      setGeneratingType(null);
    }
  };

  return (
    <article className="panel" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div className="panel-heading" style={{ marginBottom: "0" }}>
        <div>
          <h3 style={{ fontSize: "20px", fontWeight: "750", color: "var(--text-primary)" }}>{collection.name}</h3>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginTop: "4px" }}>{collection.description || "No description provided."}</p>
        </div>
        <div className="status-badge status-info">
          {collection.document_count} docs
        </div>
      </div>

      <div style={{ display: "flex", gap: "8px" }}>
        <button className="button button-ghost" style={{ flex: 1, height: "36px", fontSize: "13px" }} onClick={() => onRename(collection)}>
          Rename
        </button>
        <button className="button button-danger" style={{ flex: 1, height: "36px", fontSize: "13px" }} onClick={() => onDelete(collection.id)}>
          Delete
        </button>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", borderTop: "1px solid var(--border)", paddingTop: "16px" }}>
        <span className="eyebrow" style={{ width: "100%", fontSize: "10px", marginBottom: "4px" }}>Generate Study Products</span>
        {["Study Guide", "Briefing Doc", "FAQ", "Timeline", "Glossary", "Flashcards"].map((label) => {
          const type = label.toLowerCase().replace(" ", "-");
          return (
            <button
              key={type}
              disabled={generatingType !== null || documents.length === 0}
              className="button button-ghost"
              style={{ fontSize: "11px", height: "28px", padding: "0 8px", background: "var(--surface-card)" }}
              onClick={() => handleGenerateProduct(type, label)}
            >
              {generatingType === type ? "Generating..." : label}
            </button>
          );
        })}
      </div>

      <div className="stack" style={{ gap: "12px", borderTop: "1px solid var(--border)", paddingTop: "24px" }}>
        <span className="eyebrow" style={{ fontSize: "10px" }}>Contents</span>
        {documents.length ? (
          documents.map((document) => (
            <div key={document.id} className="surface-card" style={{ 
              padding: "12px", 
              background: "var(--surface-muted)", 
              border: "1px solid var(--border)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "12px"
            }}>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontWeight: "600", fontSize: "14px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{document.title}</div>
                <div className="mono" style={{ fontSize: "10px", opacity: 0.5 }}>{document.id.slice(0, 8)}</div>
              </div>
              <select
                style={{ height: "28px", fontSize: "11px", width: "110px", padding: "0 4px" }}
                aria-label={`Move ${document.title}`}
                defaultValue=""
                onChange={(event) => {
                  if (!event.target.value) {
                    return;
                  }
                  onMoveDocument(document.id, [event.target.value]);
                  event.target.value = "";
                }}
              >
                <option value="">Move to…</option>
                {allCollections
                  .filter((candidate) => candidate.id !== collection.id)
                  .map((candidate) => (
                    <option key={candidate.id} value={candidate.id}>
                      {candidate.name}
                    </option>
                  ))}
              </select>
            </div>
          ))
        ) : (
          <p style={{ fontSize: "13px", color: "var(--text-muted)", fontStyle: "italic" }}>No documents in this collection.</p>
        )}
      </div>

      {productResult && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          zIndex: 9999,
          padding: "24px"
        }} onClick={() => setProductResult(null)}>
          <div style={{
            backgroundColor: "var(--surface)",
            color: "var(--text-primary)",
            padding: "24px",
            borderRadius: "var(--radius-lg)",
            width: "100%",
            maxWidth: "700px",
            maxHeight: "85vh",
            display: "flex",
            flexDirection: "column",
            gap: "16px",
            border: "1px solid var(--border)",
            boxShadow: "var(--shadow-xl)"
          }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <h3 style={{ margin: 0, fontSize: "18px", fontWeight: "700" }}>{productResult.title}</h3>
              <button 
                onClick={() => setProductResult(null)} 
                className="button button-ghost" 
                style={{ height: "28px", padding: "0 10px" }}
              >
                Close
              </button>
            </div>
            
            <div style={{ flex: 1, overflowY: "auto", fontSize: "14px", lineHeight: "1.6", whiteSpace: "pre-wrap" }}>
              {productResult.type === "flashcards" ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  {productResult.data.map((card, cidx) => (
                    <div key={cidx} className="surface-card" style={{ padding: "14px", border: "1px solid var(--border)", background: "var(--surface-muted)" }}>
                      <div style={{ fontWeight: "600", color: "var(--accent-strong)", marginBottom: "4px" }}>Question: {card.question}</div>
                      <div style={{ color: "var(--text-secondary)" }}>Answer: {card.answer}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div>{productResult.data.content}</div>
              )}
            </div>
          </div>
        </div>
      )}
    </article>
  );
}

export default CollectionCard;
