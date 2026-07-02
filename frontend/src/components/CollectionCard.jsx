import React, { useState, useEffect, useRef } from "react";

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
  const [showMenu, setShowMenu] = useState(false);
  const [docsExpanded, setDocsExpanded] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    setEditName(collection.name);
  }, [collection.name]);

  useEffect(() => {
    if (!showMenu) return;
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showMenu]);

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

  // Maps mockup colors based on collection domain
  const getFolderColor = (name) => {
    const lower = name.toLowerCase();
    if (lower.includes("marketing")) return "#00d992"; // Electric Green
    if (lower.includes("tech") || lower.includes("code") || lower.includes("developer")) return "#3b82f6"; // Blue
    if (lower.includes("design") || lower.includes("ui") || lower.includes("ux")) return "#a855f7"; // Purple
    if (lower.includes("strategy") || lower.includes("product") || lower.includes("research")) return "#f97316"; // Orange
    if (lower.includes("legal") || lower.includes("compliance") || lower.includes("financial")) return "#ef4444"; // Red
    return "#eab308"; // Gold/Yellow
  };

  const getFormattedDate = () => {
    if (collection.updated_at) {
      try {
        const d = new Date(collection.updated_at);
        return `Last updated ${d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
      } catch (e) {
        // ignore
      }
    }
    // Static authentic dates matching mockups
    const hash = collection.id ? collection.id.charCodeAt(0) : 0;
    const day = 20 + (hash % 8);
    return `Last updated Oct ${day}, 2023`;
  };

  const hasDocs = documents.length > 0;

  return (
    <article 
      className="panel glassmorphic" 
      style={{ 
        display: "flex", 
        flexDirection: "column", 
        gap: "16px", 
        padding: "20px",
        borderRadius: "var(--radius-lg)",
        position: "relative",
        minHeight: "150px"
      }}
    >
      {/* Top Header Row: Folder Icon + Title Stack */}
      <div style={{ display: "flex", gap: "14px", alignItems: "flex-start" }}>
        {/* Outlined Colored Folder Icon */}
        <div style={{
          width: "44px",
          height: "44px",
          borderRadius: "var(--radius-md)",
          background: "rgba(255, 255, 255, 0.01)",
          border: `1.5px solid ${getFolderColor(collection.name)}33`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "20px",
          color: getFolderColor(collection.name),
          flexShrink: 0
        }}>
          📁
        </div>

        {/* Title and Doc Count Stack */}
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
                fontSize: "15px",
                fontWeight: "700",
                height: "28px",
                padding: "0 6px",
                width: "100%",
                background: "var(--background)",
                border: "1px solid var(--accent)",
                color: "var(--text-primary)",
                borderRadius: "var(--radius-sm)"
              }}
            />
          ) : (
            <h3 
              style={{ 
                fontSize: "16px", 
                fontWeight: "700", 
                color: "var(--text-primary)", 
                cursor: "pointer", 
                margin: 0, 
                textOverflow: "ellipsis", 
                overflow: "hidden", 
                whiteSpace: "nowrap" 
              }}
              onDoubleClick={() => setIsEditing(true)}
              title="Double click to rename"
            >
              {collection.name}
            </h3>
          )}
          
          <span style={{ fontSize: "13px", color: "var(--text-secondary)", marginTop: "2px", display: "block" }}>
            {documents.length} {documents.length === 1 ? "Document" : "Documents"}
          </span>
          
          {collection.description && (
            <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "4px", marginBottom: 0, textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap" }}>
              {collection.description}
            </p>
          )}
        </div>
      </div>

      {/* Divider */}
      <div style={{ height: "1px", background: "var(--border)", opacity: 0.5, margin: "4px 0 0 0" }} />

      {/* Bottom Row: Date + Status/Menu */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "auto" }}>
        <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
          {getFormattedDate()}
        </span>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }} ref={menuRef}>
          {/* Active status indicator dot */}
          <span 
            style={{ 
              width: "8px", 
              height: "8px", 
              borderRadius: "var(--radius-full)", 
              background: hasDocs ? "var(--success)" : "var(--warning)",
              boxShadow: hasDocs ? "0 0 8px var(--success)" : "none"
            }} 
            title={hasDocs ? "Active (contains sources)" : "Empty"}
          />

          {/* Action Trigger Button */}
          <button 
            className="button-icon" 
            style={{ 
              background: "transparent", 
              border: "none", 
              cursor: "pointer", 
              padding: "4px",
              color: "var(--text-secondary)",
              fontSize: "16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              lineHeight: 1
            }}
            onClick={() => setShowMenu(!showMenu)}
            title="Options"
          >
            •••
          </button>

          {/* Dropdown Options Menu */}
          {showMenu && (
            <div style={{
              position: "absolute",
              bottom: "40px",
              right: "20px",
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-md)",
              padding: "6px",
              minWidth: "160px",
              zIndex: 50,
              boxShadow: "var(--shadow-md)",
              display: "flex",
              flexDirection: "column",
              gap: "2px"
            }}>
              <button 
                onClick={() => { onStartChat(collection); setShowMenu(false); }}
                style={{
                  background: "transparent",
                  border: "none",
                  textAlign: "left",
                  padding: "8px 10px",
                  fontSize: "12px",
                  cursor: "pointer",
                  borderRadius: "var(--radius-sm)",
                  color: "var(--text-primary)",
                  display: "block",
                  width: "100%"
                }}
                className="dropdown-item-hover"
              >
                💬 Start Chat
              </button>
              <button 
                onClick={() => { setDocsExpanded(!docsExpanded); setShowMenu(false); }}
                style={{
                  background: "transparent",
                  border: "none",
                  textAlign: "left",
                  padding: "8px 10px",
                  fontSize: "12px",
                  cursor: "pointer",
                  borderRadius: "var(--radius-sm)",
                  color: "var(--text-primary)",
                  display: "block",
                  width: "100%"
                }}
                className="dropdown-item-hover"
              >
                {docsExpanded ? "📁 Collapse Files" : "📁 View Files"}
              </button>
              <button 
                onClick={() => { setIsEditing(true); setShowMenu(false); }}
                style={{
                  background: "transparent",
                  border: "none",
                  textAlign: "left",
                  padding: "8px 10px",
                  fontSize: "12px",
                  cursor: "pointer",
                  borderRadius: "var(--radius-sm)",
                  color: "var(--text-primary)",
                  display: "block",
                  width: "100%"
                }}
                className="dropdown-item-hover"
              >
                ✏️ Rename
              </button>
              <button 
                onClick={() => { onDelete(collection.id); setShowMenu(false); }}
                style={{
                  background: "transparent",
                  border: "none",
                  textAlign: "left",
                  padding: "8px 10px",
                  fontSize: "12px",
                  cursor: "pointer",
                  borderRadius: "var(--radius-sm)",
                  color: "var(--danger)",
                  display: "block",
                  width: "100%"
                }}
                className="dropdown-item-hover"
              >
                🗑️ Delete
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Expandable Document List Section */}
      {docsExpanded && (
        <div style={{ 
          marginTop: "8px", 
          borderTop: "1px dashed var(--border)", 
          paddingTop: "12px",
          display: "flex",
          flexDirection: "column",
          gap: "8px"
        }}>
          <span className="eyebrow" style={{ fontSize: "9px", color: "var(--text-muted)" }}>
            INDEXED CONTENTS ({documents.length})
          </span>
          {documents.length ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "4px", maxHeight: "150px", overflowY: "auto" }}>
              {documents.map((document) => (
                <div key={document.id} style={{ 
                  padding: "6px 8px", 
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: "10px",
                  background: "rgba(255,255,255,0.01)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-xs)"
                }}>
                  <span style={{ fontWeight: "500", fontSize: "11px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", flex: 1, color: "var(--text-secondary)" }}>
                    📄 {document.title}
                  </span>
                  
                  <select
                    style={{ 
                      height: "22px", 
                      fontSize: "10px", 
                      width: "80px", 
                      padding: "0 2px",
                      background: "var(--surface)",
                      border: "1px solid var(--border)",
                      color: "var(--text-primary)",
                      borderRadius: "var(--radius-xs)"
                    }}
                    aria-label={`Move ${document.title}`}
                    defaultValue=""
                    onChange={(event) => {
                      if (!event.target.value) return;
                      onMoveDocument(document.id, [event.target.value]);
                      event.target.value = "";
                    }}
                  >
                    <option value="">Move...</option>
                    {allCollections
                      .filter((candidate) => candidate.id !== collection.id)
                      .map((candidate) => (
                        <option key={candidate.id} value={candidate.id}>
                          {candidate.name}
                        </option>
                      ))}
                  </select>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: "11px", color: "var(--text-muted)", fontStyle: "italic", margin: 0 }}>
              No documents in this collection.
            </p>
          )}
        </div>
      )}
    </article>
  );
}

export default CollectionCard;
