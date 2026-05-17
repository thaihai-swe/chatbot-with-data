import { useState } from "react";

function CollectionForm({ onSubmit }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    if (!name.trim()) {
      return;
    }
    await onSubmit({ name, description });
    setName("");
    setDescription("");
  }

  return (
    <section className="panel" style={{ background: "var(--accent-soft)", border: "1px solid var(--accent)", boxShadow: "var(--shadow-sm)" }}>
      <div className="panel-heading" style={{ marginBottom: "24px" }}>
        <div>
          <h2 style={{ fontSize: "20px", fontWeight: "750" }}>Create Architecture</h2>
          <p style={{ color: "var(--text-secondary)" }}>Define a new collection to structure your knowledge retrieval.</p>
        </div>
      </div>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        <div className="grid" style={{ gridTemplateColumns: "1fr 2fr", gap: "24px" }}>
          <div className="field" style={{ marginBottom: 0 }}>
            <label htmlFor="collection-name">Collection Name</label>
            <input 
              id="collection-name"
              placeholder="e.g. Technical Specs"
              value={name} 
              onChange={(event) => setName(event.target.value)} 
              style={{ background: "var(--surface)" }}
            />
          </div>
          <div className="field" style={{ marginBottom: 0 }}>
            <label htmlFor="collection-desc">Purpose / Description</label>
            <input 
              id="collection-desc"
              placeholder="Optional context for this collection..."
              value={description} 
              onChange={(event) => setDescription(event.target.value)} 
              style={{ background: "var(--surface)" }}
            />
          </div>
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button className="button button-primary" type="submit" disabled={!name.trim()} style={{ height: "44px", padding: "0 32px" }}>
            <span>➕</span> Build Collection
          </button>
        </div>
      </form>
    </section>
  );
}

export default CollectionForm;
