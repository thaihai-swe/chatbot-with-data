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
        <h2>Document inventory</h2>
        <p>No documents are stored yet. Upload a source to create your first record.</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <h2>Document inventory</h2>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Document ID</th>
              <th>Source type</th>
              <th>Collections</th>
              <th>Status</th>
              <th>Duplicate state</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((document) => (
              <tr key={document.id}>
                <td>{document.title}</td>
                <td className="mono">{document.id}</td>
                <td>{document.source_type}</td>
                <td>
                  {(document.collections || []).map((collection) => collection.name).join(", ") ||
                    "None"}
                </td>
                <td>
                  <StatusBadge status={document.latest_status} />
                </td>
                <td>{document.latest_duplicate_status || "unique"}</td>
                <td>
                  <div className="action-stack">
                    <button
                      className="button button-ghost"
                      type="button"
                      onClick={() => onReingest(document)}
                    >
                      Re-ingest
                    </button>
                    <select
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
