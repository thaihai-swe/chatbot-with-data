import { apiRequest } from "./client";

export function listCollections() {
  return apiRequest("/collections");
}

export function createCollection(payload) {
  return apiRequest("/collections", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateCollection(collectionId, payload) {
  return apiRequest(`/collections/${collectionId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteCollection(collectionId) {
  return apiRequest(`/collections/${collectionId}`, { method: "DELETE" });
}

export function listDocuments({ collectionId = "", query = "" } = {}) {
  const params = new URLSearchParams();
  if (collectionId) {
    params.set("collection_id", collectionId);
  }
  if (query) {
    params.set("query", query);
  }
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return apiRequest(`/documents${suffix}`);
}

export function deleteDocument(documentId) {
  return apiRequest(`/documents/${documentId}`, { method: "DELETE" });
}

export function moveDocument(documentId, collectionIds) {
  return apiRequest(`/documents/${documentId}/move`, {
    method: "POST",
    body: JSON.stringify({ collection_ids: collectionIds }),
  });
}

export function reingestDocument(documentId, collectionIds) {
  return apiRequest(`/documents/${documentId}/reingest`, {
    method: "POST",
    body: JSON.stringify({ collection_ids: collectionIds }),
  });
}

export function uploadFile({ file, collectionId }) {
  const body = new FormData();
  body.append("file", file);
  if (collectionId) {
    body.append("collection_ids", collectionId);
  }
  return apiRequest("/ingestion/file-upload", {
    method: "POST",
    body,
  });
}

export function submitUrl({ url, collectionIds }) {
  return apiRequest("/ingestion/url", {
    method: "POST",
    body: JSON.stringify({ url, collection_ids: collectionIds }),
  });
}

export function listIngestionAttempts(status = "") {
  const suffix = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiRequest(`/ingestion/attempts${suffix}`);
}

export function getIngestionAttempt(attemptId) {
  return apiRequest(`/ingestion/attempts/${attemptId}`);
}

export function decideDuplicate(attemptId, action) {
  return apiRequest(`/ingestion/attempts/${attemptId}/duplicate-decision`, {
    method: "POST",
    body: JSON.stringify({ action }),
  });
}
