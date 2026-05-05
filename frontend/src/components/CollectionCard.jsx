function CollectionCard({
  collection,
  documents,
  allCollections,
  onRename,
  onDelete,
  onMoveDocument,
}) {
  return (
    <article className="surface-card">
      <div className="panel-heading">
        <div>
          <h3>{collection.name}</h3>
          <p>{collection.description || "No description"}</p>
        </div>
        <div className="stats">
          <span>{collection.document_count} document(s)</span>
        </div>
      </div>
      <div className="action-row">
        <button className="button button-ghost" onClick={() => onRename(collection)}>
          Rename
        </button>
        <button className="button button-danger" onClick={() => onDelete(collection.id)}>
          Delete
        </button>
      </div>
      <div className="member-list">
        {documents.length ? (
          documents.map((document) => (
            <div className="member-row" key={document.id}>
              <div>
                <strong>{document.title}</strong>
                <p className="mono">{document.id}</p>
              </div>
              <select
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
          <p>This collection does not contain any documents yet.</p>
        )}
      </div>
    </article>
  );
}

export default CollectionCard;
