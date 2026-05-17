import StatusBadge from "./StatusBadge";

function DocumentTable({
  collections,
  documents,
  onDelete,
  onReingest,
  onMove,
}) {
  if (!documents.length) {
    return (
      <section className="panel">
        <div className="empty-state">
          <h3 style={{ fontSize: "20px", marginBottom: "12px", color: "var(--text-primary)" }}>No documents found</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "15px" }}>Upload a source above to populate your library.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="panel" style={{ padding: "0", overflow: "hidden" }}>
      <div style={{ padding: "32px 32px 0" }}>
        <h2 style={{ fontSize: "20px", marginBottom: "8px" }}>Library Inventory</h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginBottom: "24px" }}>Manage and organize your indexed source documents.</p>
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Document Title</th>
              <th>Source</th>
              <th>Collection</th>
              <th>Status</th>
              <th style={{ textAlign: "right" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((document) => (
              <tr key={document.id}>
                <td style={{ fontWeight: "650", color: "var(--text-primary)" }}>{document.title}</td>
                <td className="mono" style={{ fontSize: "11px", opacity: 0.7 }}>{document.source_type.toUpperCase()}</td>
                <td style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                  {(document.collections || []).map((collection) => collection.name).join(", ") ||
                    "None"}
                </td>
                <td>
                  <StatusBadge status={document.latest_status} />
                </td>
                <td>
                  <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
                    <button
                      className="button button-ghost"
                      style={{ height: "32px", padding: "0 10px", fontSize: "12px" }}
                      type="button"
                      onClick={() => onReingest(document)}
                    >
                      Re-ingest
                    </button>
                    <select
                      style={{ width: "160px", height: "32px", fontSize: "12px", padding: "0 8px" }}
                      aria-label={`Move ${document.title} to collection`}
                      defaultValue=""
                      onChange={(event) => {
                        if (!event.target.value) {
                          return;
                        }
                        onMove(document, [event.target.value]);
                        event.target.value = "";
                      }}
                    >
                      <option value="">Move to collection</option>
                      {collections.map((collection) => (
                        <option key={collection.id} value={collection.id}>
                          {collection.name}
                        </option>
                      ))}
                    </select>
                    <button
                      className="button button-danger"
                      style={{ height: "32px", padding: "0 10px", fontSize: "12px" }}
                      type="button"
                      onClick={() => onDelete(document.id)}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default DocumentTable;
