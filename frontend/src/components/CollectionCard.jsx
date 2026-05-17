function CollectionCard({
  collection,
  documents,
  allCollections,
  onRename,
  onDelete,
  onMoveDocument,
}) {
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
