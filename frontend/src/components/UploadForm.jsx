import { useState } from "react";

function UploadForm({ collections, onUploadFile, onSubmitUrl }) {
  const [selectedCollection, setSelectedCollection] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [url, setUrl] = useState("");

  async function handleFileSubmit(event) {
    event.preventDefault();
    if (!selectedFile) {
      return;
    }
    await onUploadFile({
      file: selectedFile,
      collectionId: selectedCollection,
    });
    setSelectedFile(null);
    event.target.reset();
  }

  async function handleUrlSubmit(event) {
    event.preventDefault();
    if (!url) {
      return;
    }
    await onSubmitUrl({
      url,
      collectionIds: selectedCollection ? [selectedCollection] : [],
    });
    setUrl("");
  }

  return (
    <section className="panel" style={{ border: "1px solid var(--accent)", boxShadow: "var(--shadow-glow)" }}>
      <div className="panel-heading">
        <div>
          <h2>Ingest new knowledge</h2>
          <p>Expand your knowledge base by uploading documents or fetching web content.</p>
        </div>
      </div>
      
      <div className="field" style={{ maxWidth: "400px", marginBottom: "32px" }}>
        <label htmlFor="collection-select">Target Collection</label>
        <select
          id="collection-select"
          aria-label="Collection selection"
          value={selectedCollection}
          onChange={(event) => setSelectedCollection(event.target.value)}
        >
          <option value="">No collection selected (Default)</option>
          {collections.map((collection) => (
            <option key={collection.id} value={collection.id}>
              {collection.name}
            </option>
          ))}
        </select>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "24px" }}>
        <form className="surface-card" onSubmit={handleFileSubmit} style={{ background: "var(--surface-muted)", border: "1px dashed var(--border-strong)" }}>
          <h3 style={{ fontSize: "18px", marginBottom: "16px" }}>Upload Document</h3>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "20px" }}>PDF, TXT, or Markdown up to 10MB.</p>
          <div className="field">
            <input
              aria-label="File upload"
              accept=".pdf,.txt,.md,.markdown"
              type="file"
              onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
              style={{ padding: "8px", height: "auto" }}
            />
          </div>
          <button className="button button-primary" type="submit" disabled={!selectedFile} style={{ width: "100%", marginTop: "8px" }}>
            <span>📤</span> Ingest Document
          </button>
        </form>

        <form className="surface-card" onSubmit={handleUrlSubmit} style={{ background: "var(--surface-muted)", border: "1px dashed var(--border-strong)" }}>
          <h3 style={{ fontSize: "18px", marginBottom: "16px" }}>Fetch Web Page</h3>
          <p style={{ fontSize: "14px", color: "var(--text-secondary)", marginBottom: "20px" }}>Provide a URL to crawl and index its content.</p>
          <div className="field">
            <input
              aria-label="Source URL"
              placeholder="https://example.com/article"
              type="url"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
            />
          </div>
          <button className="button button-primary" type="submit" disabled={!url} style={{ width: "100%", marginTop: "8px" }}>
            <span>🌐</span> Fetch URL
          </button>
        </form>
      </div>
    </section>
  );
}

export default UploadForm;
