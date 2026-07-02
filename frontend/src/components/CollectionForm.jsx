import { useState } from "react";

function CollectionForm({ onSubmit, onCancel }) {
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
    <section style={{ background: "transparent", border: "none", boxShadow: "none", padding: 0 }}>
      <div className="panel-heading" style={{ marginBottom: "24px" }}>
        <div>
          <h2 style={{ fontSize: "20px", fontWeight: "750", color: "var(--text-primary)" }}>New Collection</h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "13px" }}>Define a new collection to structure your knowledge retrieval boundary.</p>
        </div>
      </div>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div className="field" style={{ marginBottom: 0, display: "flex", flexDirection: "column", gap: "6px" }}>
            <label htmlFor="collection-name" style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>
              Collection Name
            </label>
            <input 
              id="collection-name"
              placeholder="e.g. Q3 Financials 2023"
              value={name} 
              onChange={(event) => setName(event.target.value)} 
              style={{ 
                background: "var(--background)", 
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-md)",
                padding: "10px 14px",
                fontSize: "14px",
                color: "var(--text-primary)"
              }}
              required
              autoFocus
            />
          </div>
          
          <div className="field" style={{ marginBottom: 0, display: "flex", flexDirection: "column", gap: "6px" }}>
            <label htmlFor="collection-desc" style={{ fontSize: "12px", fontWeight: "600", color: "var(--text-secondary)" }}>
              Purpose / Description
            </label>
            <input 
              id="collection-desc"
              placeholder="Optional context for these materials..."
              value={description} 
              onChange={(event) => setDescription(event.target.value)} 
              style={{ 
                background: "var(--background)", 
                border: "1px solid var(--border)",
                borderRadius: "var(--radius-md)",
                padding: "10px 14px",
                fontSize: "14px",
                color: "var(--text-primary)"
              }}
            />
          </div>
        </div>
        
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "12px", marginTop: "8px" }}>
          {onCancel && (
            <button 
              className="button button-secondary" 
              type="button" 
              onClick={onCancel}
              style={{ height: "40px", padding: "0 20px" }}
            >
              Cancel
            </button>
          )}
          <button 
            className="button button-primary" 
            type="submit" 
            disabled={!name.trim()} 
            style={{ 
              height: "40px", 
              padding: "0 24px",
              background: "var(--accent)",
              color: "white",
              border: "none",
              borderRadius: "var(--radius-md)"
            }}
          >
            Create Collection
          </button>
        </div>
      </form>
    </section>
  );
}

export default CollectionForm;
