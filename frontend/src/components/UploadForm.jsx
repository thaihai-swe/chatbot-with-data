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
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>Ingest new knowledge</h2>
          <p>Upload PDF, TXT, or Markdown files, or fetch a web page by URL.</p>
        </div>
      </div>
      <label className="field">
        <span>Collection</span>
        <select
          aria-label="Collection selection"
          value={selectedCollection}
          onChange={(event) => setSelectedCollection(event.target.value)}
        >
          <option value="">No collection selected</option>
          {collections.map((collection) => (
            <option key={collection.id} value={collection.id}>
              {collection.name}
            </option>
          ))}
        </select>
      </label>
      <div className="split-panel">
        <form className="surface-card" onSubmit={handleFileSubmit}>
          <h3>Upload file</h3>
          <label className="field">
            <span>Supported files</span>
            <input
              aria-label="File upload"
              accept=".pdf,.txt,.md,.markdown"
              type="file"
              onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
            />
          </label>
          <button className="button" type="submit">
            Submit file
          </button>
        </form>
        <form className="surface-card" onSubmit={handleUrlSubmit}>
          <h3>Ingest URL</h3>
          <label className="field">
            <span>Source URL</span>
            <input
              aria-label="Source URL"
              placeholder="https://example.com/docs"
              type="url"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
            />
          </label>
          <button className="button" type="submit">
            Submit URL
          </button>
        </form>
      </div>
    </section>
  );
}

export default UploadForm;
