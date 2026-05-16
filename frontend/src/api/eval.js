/**
 * API client for evaluation operations.
 */

const API_BASE_URL = "/api";

export async function listDatasets() {
  const response = await fetch(`${API_BASE_URL}/eval/datasets`);
  if (!response.ok) throw new Error("Failed to list datasets");
  return response.json();
}

export async function getDataset(datasetId) {
  const response = await fetch(`${API_BASE_URL}/eval/datasets/${datasetId}`);
  if (!response.ok) throw new Error("Failed to get dataset");
  return response.json();
}

export async function saveDataset(dataset) {
  const response = await fetch(`${API_BASE_URL}/eval/datasets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dataset),
  });
  if (!response.ok) throw new Error("Failed to save dataset");
  return response.json();
}

export async function listRuns() {
  const response = await fetch(`${API_BASE_URL}/eval/runs`);
  if (!response.ok) throw new Error("Failed to list runs");
  return response.json();
}

export async function getRun(runId) {
  const response = await fetch(`${API_BASE_URL}/eval/runs/${runId}`);
  if (!response.ok) throw new Error("Failed to get run");
  return response.json();
}

export async function triggerRun(datasetId, config) {
  const response = await fetch(`${API_BASE_URL}/eval/run/${datasetId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  if (!response.ok) throw new Error("Failed to trigger evaluation run");
  return response.json();
}
