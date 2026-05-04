const API_BASE =
  window.location.protocol === "http:" || window.location.protocol === "https:"
    ? `${window.location.origin}/api`
    : "http://127.0.0.1:5000/api";

const collectionState = {
  selectedCollectionId: null,
  collections: [],
};

function setCollectionsStatus(message, tone = "") {
  const banner = document.getElementById("collections-status");
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

async function collectionsFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "Request failed");
  }
  return payload;
}

async function loadCollections() {
  const payload = await collectionsFetch("/collections");
  collectionState.collections = payload.items || [];
  renderCollections(collectionState.collections);
  if (collectionState.selectedCollectionId) {
    const selected = collectionState.collections.find(
      (item) => item.collection_id === collectionState.selectedCollectionId
    );
    if (selected) {
      selectCollection(selected);
    }
  }
}

function renderCollections(collections) {
  const body = document.getElementById("collections-body");
  body.innerHTML = "";
  if (!collections.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="6" class="table-empty">No collections created yet.</td>';
    body.appendChild(row);
    return;
  }
  collections.forEach((collection) => {
    const row = document.createElement("tr");
    row.dataset.collectionId = collection.collection_id;
    row.innerHTML = `
      <td>
        ${escapeHtml(collection.name)}
        ${collection.is_default ? '<span class="pill">Default</span>' : ""}
      </td>
      <td><code>${escapeHtml(collection.collection_id)}</code></td>
      <td>${collection.document_count ?? 0}</td>
      <td>${collection.chunk_count ?? 0}</td>
      <td>${escapeHtml(collection.updated_at || "-")}</td>
      <td>
        <div class="actions">
          <button type="button" class="secondary" data-action="default" data-collection-id="${escapeHtml(collection.collection_id)}">Set Default</button>
          <button type="button" class="secondary" data-action="edit" data-collection-id="${escapeHtml(collection.collection_id)}">Edit</button>
          <button type="button" class="warning" data-action="delete" data-collection-id="${escapeHtml(collection.collection_id)}">Delete</button>
        </div>
      </td>
    `;
    body.appendChild(row);
  });
}

function showSelectedCollection(collection) {
  document.getElementById("selected-collection-empty").hidden = true;
  document.getElementById("selected-collection-panel").hidden = false;
  document.getElementById("selected-collection-name").textContent = collection.name;
  document.getElementById("selected-collection-id").textContent = collection.collection_id;
  document.getElementById("selected-document-count").textContent = collection.document_count ?? 0;
  document.getElementById("selected-chunk-count").textContent = collection.chunk_count ?? 0;
  document.getElementById("selected-last-updated").textContent = collection.updated_at || "-";
  document.getElementById("selected-routing-description").textContent =
    collection.routing_description || collection.description || "";
}

async function loadDocumentsForSelectedCollection() {
  if (!collectionState.selectedCollectionId) {
    return;
  }
  const payload = await collectionsFetch(`/documents?collection_id=${encodeURIComponent(collectionState.selectedCollectionId)}`);
  renderCollectionDocuments(payload.items || []);
}

function buildCollectionOptions(currentCollectionId) {
  return collectionState.collections
    .filter((item) => item.collection_id !== currentCollectionId)
    .map(
      (item) =>
        `<option value="${escapeHtml(item.collection_id)}">${escapeHtml(item.name)}</option>`
    )
    .join("");
}

function renderCollectionDocuments(documents) {
  const body = document.getElementById("collection-documents-body");
  body.innerHTML = "";
  if (!documents.length) {
    const row = document.createElement("tr");
    row.innerHTML = '<td colspan="4" class="table-empty">No documents are assigned to this collection.</td>';
    body.appendChild(row);
    return;
  }
  documents.forEach((documentItem) => {
    const row = document.createElement("tr");
    const options = buildCollectionOptions(documentItem.collection_id);
    row.innerHTML = `
      <td>${escapeHtml(documentItem.title || "-")}</td>
      <td><code>${escapeHtml(documentItem.document_id)}</code></td>
      <td>${escapeHtml(documentItem.ingestion_status)}</td>
      <td>
        <div class="actions">
          <select data-document-id="${escapeHtml(documentItem.document_id)}">
            <option value="">Choose collection</option>
            ${options}
          </select>
          <button type="button" data-action="move-document" data-document-id="${escapeHtml(documentItem.document_id)}">Move</button>
        </div>
      </td>
    `;
    body.appendChild(row);
  });
}

async function selectCollection(collection) {
  collectionState.selectedCollectionId = collection.collection_id;
  showSelectedCollection(collection);
  await loadDocumentsForSelectedCollection();
}

async function handleCollectionFormSubmit(event) {
  event.preventDefault();
  const name = document.getElementById("collection-name").value.trim();
  const description = document.getElementById("collection-description").value.trim();
  if (!name) {
    setCollectionsStatus("Collection name is required.", "error");
    return;
  }

  try {
    await collectionsFetch("/collections", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, description }),
    });
    event.target.reset();
    setCollectionsStatus("Collection created.", "success");
    await loadCollections();
  } catch (error) {
    setCollectionsStatus(error.message, "error");
  }
}

async function handleCollectionsTableClick(event) {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }

  const button = target.closest("button");
  const row = target.closest("tr");
  if (row && !button) {
    const collection = collectionState.collections.find(
      (item) => item.collection_id === row.dataset.collectionId
    );
    if (collection) {
      await selectCollection(collection);
    }
    return;
  }

  if (!(button instanceof HTMLButtonElement)) {
    return;
  }

  const collectionId = button.dataset.collectionId;
  const action = button.dataset.action;
  const collection = collectionState.collections.find(
    (item) => item.collection_id === collectionId
  );
  if (!collection) {
    return;
  }

  try {
    if (action === "default") {
      await collectionsFetch(`/collections/${collectionId}/default`, { method: "PATCH" });
      setCollectionsStatus("Default collection updated.", "success");
    } else if (action === "edit") {
      const nextName = window.prompt("Collection name", collection.name);
      if (!nextName) {
        return;
      }
      await collectionsFetch(`/collections/${collectionId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: nextName,
          description: collection.description || "",
          routing_description: collection.routing_description || "",
        }),
      });
      setCollectionsStatus("Collection updated.", "success");
    } else if (action === "delete") {
      const confirmed = window.confirm(`Delete collection ${collection.name}?`);
      if (!confirmed) {
        return;
      }
      await collectionsFetch(`/collections/${collectionId}`, { method: "DELETE" });
      if (collectionState.selectedCollectionId === collectionId) {
        collectionState.selectedCollectionId = null;
        document.getElementById("selected-collection-empty").hidden = false;
        document.getElementById("selected-collection-panel").hidden = true;
        document.getElementById("collection-documents-body").innerHTML = "";
      }
      setCollectionsStatus("Collection deleted.", "success");
    }
    await loadCollections();
  } catch (error) {
    setCollectionsStatus(error.message, "error");
  }
}

async function handleDocumentMove(event) {
  const target = event.target;
  if (!(target instanceof HTMLButtonElement) || target.dataset.action !== "move-document") {
    return;
  }

  const documentId = target.dataset.documentId;
  const select = target.parentElement.querySelector("select");
  const nextCollectionId = select.value;
  if (!nextCollectionId) {
    setCollectionsStatus("Choose a target collection first.", "error");
    return;
  }

  try {
    await collectionsFetch(`/documents/${documentId}/collection`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ collection_id: nextCollectionId }),
    });
    setCollectionsStatus("Document moved.", "success");
    await loadCollections();
    await loadDocumentsForSelectedCollection();
  } catch (error) {
    setCollectionsStatus(error.message, "error");
  }
}

document.getElementById("collection-form").addEventListener("submit", handleCollectionFormSubmit);
document.getElementById("collections-body").addEventListener("click", (event) => {
  handleCollectionsTableClick(event).catch((error) => setCollectionsStatus(error.message, "error"));
});
document.getElementById("collection-documents-body").addEventListener("click", (event) => {
  handleDocumentMove(event).catch((error) => setCollectionsStatus(error.message, "error"));
});

loadCollections().catch((error) => setCollectionsStatus(error.message, "error"));
