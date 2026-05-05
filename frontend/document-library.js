const API_BASE =
  window.location.protocol === "http:" || window.location.protocol === "https:"
    ? `${window.location.origin}/api`
    : "http://127.0.0.1:5000/api";

const state = {
  duplicateDocumentId: null,
  highlightedDocumentId: new URL(window.location.href).searchParams.get("document_id"),
};

function setStatus(message, tone = "") {
  const banner = document.getElementById("status-banner");
  banner.textContent = message || "";
  banner.className = `status-banner ${tone}`.trim();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function openErrorModal(message) {
  document.getElementById("error-summary").textContent = message || "Unexpected request error.";
  document.getElementById("error-modal").classList.add("open");
}

function closeErrorModal() {
  document.getElementById("error-modal").classList.remove("open");
}

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || (payload.errors && payload.errors.join(", ")) || "Request failed");
  }
  return payload;
}

function populateCollectionSelect(selectId, collections, allowEmptyLabel) {
  const select = document.getElementById(selectId);
  const currentValue = select.value;
  select.innerHTML = "";

  if (allowEmptyLabel) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = allowEmptyLabel;
    select.appendChild(option);
  }

  collections.forEach((collection) => {
    const option = document.createElement("option");
    option.value = collection.collection_id;
    option.textContent = collection.name;
    select.appendChild(option);
  });

  select.value = currentValue;
}

async function loadCollections() {
  const payload = await apiFetch("/collections");
  const collections = payload.items || [];
  populateCollectionSelect("upload-collection", collections, "No collection");
  populateCollectionSelect("url-collection", collections, "No collection");
  populateCollectionSelect("filter-collection", collections, "All collections");
  return collections;
}

function formatCell(value) {
  return value || "-";
}

function renderDocuments(documents) {
  const body = document.getElementById("documents-body");
  body.innerHTML = "";

  if (!documents.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="10" class="table-empty">No documents found for the current filters.</td>';
    body.appendChild(row);
    return;
  }

  documents.forEach((documentItem) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(formatCell(documentItem.title))}</td>
      <td><code>${escapeHtml(documentItem.document_id)}</code></td>
      <td>${escapeHtml(formatCell(documentItem.source_type))}</td>
      <td>${escapeHtml(formatCell(documentItem.collection_name))}</td>
      <td><span class="pill">${escapeHtml(formatCell(documentItem.ingestion_status))}</span></td>
      <td>${escapeHtml(formatCell(documentItem.duplicate_status))}</td>
      <td>${documentItem.chunk_count ?? 0}</td>
      <td>${escapeHtml(formatCell(documentItem.created_at))}</td>
      <td>${escapeHtml(formatCell(documentItem.last_indexed_at))}</td>
      <td>
        <div class="actions">
          <button type="button" class="secondary" data-action="reindex" data-document-id="${escapeHtml(documentItem.document_id)}">Re-index</button>
          <button type="button" class="warning" data-action="delete" data-document-id="${escapeHtml(documentItem.document_id)}">Delete</button>
        </div>
      </td>
    `;
    body.appendChild(row);
  });
}

async function loadDocuments() {
  const collectionId = document.getElementById("filter-collection").value;
  const search = document.getElementById("search-input").value.trim();
  const query = new URLSearchParams();
  if (collectionId) {
    query.set("collection_id", collectionId);
  }
  if (search) {
    query.set("search", search);
  }

  const payload = await apiFetch(`/documents${query.toString() ? `?${query.toString()}` : ""}`);
  const items = payload.items || [];
  if (state.highlightedDocumentId) {
    renderDocuments(items.filter((item) => item.document_id === state.highlightedDocumentId));
    if (!items.some((item) => item.document_id === state.highlightedDocumentId)) {
      setStatus(`Document ${state.highlightedDocumentId} was not found.`, "error");
    } else {
      setStatus(`Showing cited document ${state.highlightedDocumentId}.`, "success");
    }
    return;
  }
  renderDocuments(items);
}

function openDuplicateModal(payload) {
  state.duplicateDocumentId = payload.document_id;
  document.getElementById("duplicate-summary").textContent =
    "A duplicate or near-duplicate document was detected. Choose how to continue.";
  document.getElementById("duplicate-matched-id").textContent = payload.matched_document_id || "-";
  document.getElementById("duplicate-classification").textContent = payload.duplicate_class || "-";
  document.getElementById("duplicate-score").textContent =
    payload.similarity_score == null ? "-" : String(payload.similarity_score);
  document.getElementById("duplicate-method").textContent = payload.detection_method || "-";
  document.getElementById("duplicate-modal").classList.add("open");
}

function closeDuplicateModal() {
  state.duplicateDocumentId = null;
  document.getElementById("duplicate-modal").classList.remove("open");
}

async function submitDuplicateDecision(decision) {
  if (!state.duplicateDocumentId) {
    return;
  }
  const payload = await apiFetch(`/documents/${state.duplicateDocumentId}/duplicate-decision`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision }),
  });
  setStatus(`Duplicate decision applied: ${decision}`, "success");
  closeDuplicateModal();
  await loadDocuments();
  return payload;
}

async function handleUpload(event) {
  event.preventDefault();
  setStatus("Uploading document...");
  const formData = new FormData();
  const fileInput = document.getElementById("upload-file");
  if (!fileInput.files[0]) {
    setStatus("Select a file before uploading.", "error");
    return;
  }
  formData.append("file", fileInput.files[0]);
  formData.append("collection_id", document.getElementById("upload-collection").value);

  try {
    const payload = await apiFetch("/documents/upload", {
      method: "POST",
      body: formData,
    });
    if (payload.status === "duplicate_detected") {
      openDuplicateModal(payload);
      setStatus("Duplicate detected. Choose how to continue.", "error");
    } else {
      setStatus("Document uploaded successfully.", "success");
      event.target.reset();
      await loadDocuments();
    }
  } catch (error) {
    setStatus(error.message, "error");
    openErrorModal(error.message);
  }
}

async function handleUrlIngestion(event) {
  event.preventDefault();
  const urlValue = document.getElementById("url-input").value.trim();
  try {
    new URL(urlValue);
  } catch (_error) {
    setStatus("Invalid URL format.", "error");
    return;
  }

  setStatus("Fetching URL...");
  try {
    const payload = await apiFetch("/documents/ingest-url", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: urlValue,
        collection_id: document.getElementById("url-collection").value,
      }),
    });
    if (payload.status === "duplicate_detected") {
      openDuplicateModal(payload);
      setStatus("Duplicate detected. Choose how to continue.", "error");
    } else {
      setStatus("URL ingested successfully.", "success");
      event.target.reset();
      await loadDocuments();
    }
  } catch (error) {
    setStatus(error.message, "error");
    openErrorModal(error.message);
  }
}

async function handleDocumentAction(event) {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement)) {
    return;
  }
  const documentId = target.dataset.documentId;
  const action = target.dataset.action;
  if (!documentId || !action) {
    return;
  }

  try {
    if (action === "delete") {
      const confirmed = window.confirm(`Delete document ${documentId}? This cannot be undone.`);
      if (!confirmed) {
        return;
      }
      await apiFetch(`/documents/${documentId}`, { method: "DELETE" });
      setStatus("Document deleted.", "success");
    } else if (action === "reindex") {
      setStatus("Re-indexing document...");
      await apiFetch(`/documents/${documentId}/re-index`, { method: "POST" });
      setStatus("Document re-indexed successfully.", "success");
    }
    await loadDocuments();
  } catch (error) {
    setStatus(error.message, "error");
    openErrorModal(error.message);
  }
}

document.getElementById("upload-form").addEventListener("submit", handleUpload);
document.getElementById("url-form").addEventListener("submit", handleUrlIngestion);
document.getElementById("refresh-documents").addEventListener("click", () => loadDocuments().catch((error) => setStatus(error.message, "error")));
document.getElementById("documents-body").addEventListener("click", handleDocumentAction);
document.getElementById("search-input").addEventListener("input", () => loadDocuments().catch((error) => setStatus(error.message, "error")));
document.getElementById("filter-collection").addEventListener("change", () => loadDocuments().catch((error) => setStatus(error.message, "error")));
document.querySelectorAll("[data-decision]").forEach((button) => {
  button.addEventListener("click", () => {
    submitDuplicateDecision(button.dataset.decision).catch((error) => setStatus(error.message, "error"));
  });
});
document.getElementById("duplicate-modal").addEventListener("click", (event) => {
  if (event.target.id === "duplicate-modal") {
    closeDuplicateModal();
  }
});
document.getElementById("error-close").addEventListener("click", closeErrorModal);
document.getElementById("error-modal").addEventListener("click", (event) => {
  if (event.target.id === "error-modal") {
    closeErrorModal();
  }
});

Promise.all([loadCollections(), loadDocuments()]).catch((error) => {
  setStatus(error.message, "error");
  openErrorModal(error.message);
});
