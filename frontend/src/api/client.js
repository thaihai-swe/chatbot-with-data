const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function parseJson(response) {
  const text = await response.text();
  return text ? JSON.parse(text) : null;
}

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const payload = await parseJson(response);
    const message = payload?.detail || "Request failed";
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }

  return parseJson(response);
}
