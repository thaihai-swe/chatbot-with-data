import React, { useState, useEffect } from "react";

function CollectionCard({
  collection,
  documents,
  allCollections,
  onRename,
  onDelete,
  onMoveDocument,
  onStartChat,
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(collection.name);

  useEffect(() => {
    setEditName(collection.name);
  }, [collection.name]);

  const handleSubmit = () => {
    if (editName.trim() && editName !== collection.name) {
      onRename(collection, editName.trim());
    } else {
      setEditName(collection.name);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSubmit();
    } else if (e.key === "Escape") {
      setEditName(collection.name);
      setIsEditing(false);
    }
  };

  const getCollectionIcon = (name) => {
    const lower = name.toLowerCase();
    if (lower.includes("marketing")) return "📢";
    if (lower.includes("tech") || lower.includes("code") || lower.includes("developer")) return "💻";
    if (lower.includes("design") || lower.includes("ui") || lower.includes("ux")) return "🎨";
    if (lower.includes("strategy") || lower.includes("product") || lower.includes("research")) return "🎯";
    return "📁";
  };

  return (
    <article className="panel glassmorphic" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <div style={{ display: "flex", gap: "16px", alignItems: "flex-start", marginBottom: "4px" }}>
        <div style={{
          width: "48px",
          height: "48px",
          borderRadius: "var(--radius-md)",
          background: "rgba(255, 255, 255, 0.03)",
          border: "1px solid var(--glass-border)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "24px",
          flexShrink: 0
        }}>
          {getCollectionIcon(collection.name)}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          {isEditing ? (
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={handleSubmit}
              autoFocus
              style={{
                fontSize: "18px",
                fontWeight: "750",
                height: "36px",
                padding: "0 8px",
                marginBottom: "4px",
              }}
            />
          ) : (
            <h3 
              style={{ fontSize: "20px", fontWeight: "750", color: "var(--text-primary)", cursor: "pointer", margin: 0, textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap" }}
              onDoubleClick={() => setIsEditing(true)}
              title="Double click to rename"
            >
              {collection.name}
            </h3>
          )}
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "4px", lineHeight: "1.4" }}>
            {collection.description || "No description provided."}
          </p>
          <div style={{ display: "flex", gap: "16px", marginTop: "12px", fontSize: "11px", color: "var(--text-secondary)", fontWeight: "600" }}>
            <span>📄 {collection.document_count || 0} Docs</span>
            <span>•</span>
            <span>Updated: Just now</span>
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "8px" }}>
        <button 
          className="button button-primary" 
          style={{ flex: 2, height: "36px", fontSize: "13px" }} 
          onClick={() => onStartChat(collection)}
        >
          💬 Start Chat
        </button>
        <button className="button button-ghost" style={{ flex: 1, height: "36px", fontSize: "13px" }} onClick={() => setIsEditing(true)}>
          Rename
        </button>
        <button className="button button-danger" style={{ flex: 1, height: "36px", fontSize: "13px" }} onClick={() => onDelete(collection.id)}>
          Delete
        </button>
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
    </article>
  );
}

export default CollectionCard;
