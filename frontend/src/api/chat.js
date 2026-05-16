/**
 * API client for chat operations.
 */

const API_BASE_URL = "/api"; // Assuming vite proxy or similar

export async function createChatSession(collectionId = null, metadata = {}) {
  const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ collection_id: collectionId, metadata }),
  });
  if (!response.ok) throw new Error("Failed to create chat session");
  return response.json();
}

export async function listChatSessions() {
  const response = await fetch(`${API_BASE_URL}/chat/sessions`);
  if (!response.ok) throw new Error("Failed to list chat sessions");
  return response.json();
}

export async function getChatHistory(sessionId) {
  const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/history`);
  if (!response.ok) throw new Error("Failed to get chat history");
  return response.json();
}

export async function cancelChatTurn(turnId) {
  const response = await fetch(`${API_BASE_URL}/chat/turns/${turnId}/cancel`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("Failed to cancel chat turn");
  return response.json();
}

/**
 * Stream a chat turn using SSE.
 * 
 * @param {string} sessionId 
 * @param {string} queryText 
 * @param {Object} callbacks - { onStatus, onToken, onCitations, onError, onDone }
 */
export function streamChatTurn(sessionId, queryText, advancedConfig, { 
  onStatus, 
  onToken, 
  onCitations,
  onTrace,
  onError, 
  onDone 
}) {
  const controller = new AbortController();
  
  fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/turns/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query_text: queryText, advanced_config: advancedConfig }),
    signal: controller.signal,
  }).then(async (response) => {
    if (!response.ok) {
      onError?.(new Error(`Stream error: ${response.statusText}`));
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      
      // SSE format: event: name\ndata: json\n\n
      const lines = buffer.split("\n\n");
      buffer = lines.pop(); // Keep last partial chunk

      for (const block of lines) {
        const eventMatch = block.match(/event:\s*(.+)/);
        const dataMatch = block.match(/data:\s*(.+)/);
        
        if (eventMatch && dataMatch) {
          const event = eventMatch[1].trim();
          const data = JSON.parse(dataMatch[1].trim());
          
          switch (event) {
            case "status": onStatus?.(data); break;
            case "token": onToken?.(data.content); break;
            case "citations": 
              onCitations?.(data.citations); 
              if (data.retrieval_trace || data.safety_trace) {
                // Combine traces for the debug view
                onTrace?.({
                  retrieval: data.retrieval_trace,
                  safety: data.safety_trace
                });
              }
              break;
            case "trace": onTrace?.(data); break;
            case "error": onError?.(data); break;
            case "done": onDone?.(data); break;
          }
        }
      }
    }
  }).catch((err) => {
    if (err.name === "AbortError") return;
    onError?.(err);
  });

  return () => controller.abort();
}
