const API_BASE =
  window.location.protocol === "http:" || window.location.protocol === "https:"
    ? `${window.location.origin}/api`
    : "http://127.0.0.1:5000/api";

const chatState = {
  sessionId: null,
  sessions: [],
  collections: [],
  runs: [],
  runsById: {},
  runsByTurnId: {},
  currentRunId: null,
  currentTurnId: null,
  streamReader: null,
  streamActive: false,
  partialAnswer: "",
  latestPayload: null,
  latestDebugPayload: null,
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function setChatStatus(message, tone = "") {
  const banner = document.getElementById("chat-status");
  banner.textContent = message || "";
  banner.className = `status-banner ${tone}`.trim();
}

function setAnswerStatus(label) {
  document.getElementById("answer-status").textContent = label;
}

function openChatError(message) {
  document.getElementById("chat-error-message").textContent = message || "Unexpected request error.";
  document.getElementById("chat-error-modal").classList.add("open");
}

function closeChatError() {
  document.getElementById("chat-error-modal").classList.remove("open");
}

function apiFetch(path, options = {}) {
  return fetch(`${API_BASE}${path}`, options).then(async (response) => {
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.error || (payload.errors && payload.errors.join(", ")) || "Request failed");
    }
    return payload;
  });
}

function sessionStorageKey(name) {
  return `grounded-chat:${name}`;
}

function currentQueryParam(name) {
  return new URL(window.location.href).searchParams.get(name);
}

function updateUrlSession(sessionId) {
  const url = new URL(window.location.href);
  if (sessionId) {
    url.searchParams.set("session_id", sessionId);
  } else {
    url.searchParams.delete("session_id");
  }
  window.history.replaceState({}, "", url);
}

function persistControls() {
  window.sessionStorage.setItem(sessionStorageKey("collection"), document.getElementById("chat-collection").value);
  window.sessionStorage.setItem(sessionStorageKey("retrieval-mode"), document.getElementById("retrieval-mode").value);
  window.sessionStorage.setItem(sessionStorageKey("stream-enabled"), document.getElementById("stream-toggle").checked ? "1" : "0");
  window.sessionStorage.setItem(sessionStorageKey("debug-enabled"), document.getElementById("debug-toggle").checked ? "1" : "0");
}

function restoreControls() {
  const savedCollection = window.sessionStorage.getItem(sessionStorageKey("collection"));
  const savedMode = window.sessionStorage.getItem(sessionStorageKey("retrieval-mode"));
  const savedStream = window.sessionStorage.getItem(sessionStorageKey("stream-enabled"));
  const savedDebug = window.sessionStorage.getItem(sessionStorageKey("debug-enabled"));
  if (savedMode) {
    document.getElementById("retrieval-mode").value = savedMode;
  }
  document.getElementById("stream-toggle").checked = savedStream === "1";
  document.getElementById("debug-toggle").checked = savedDebug === "1";
  document.getElementById("debug-panel").hidden = !document.getElementById("debug-toggle").checked;
  if (savedCollection != null) {
    document.getElementById("chat-collection").dataset.pendingValue = savedCollection;
  }
}

function renderSessionList() {
  const container = document.getElementById("session-list");
  container.innerHTML = "";
  if (!chatState.sessions.length) {
    container.innerHTML = '<p class="muted">No chat sessions yet.</p>';
    return;
  }

  chatState.sessions.forEach((session) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = `session-item ${session.session_id === chatState.sessionId ? "active" : ""}`.trim();
    item.dataset.sessionId = session.session_id;
    item.innerHTML = `
      <strong>${escapeHtml(session.collection_name || "All collections")}</strong>
      <span class="muted">${escapeHtml(session.retrieval_mode)}</span>
      <span class="muted">${escapeHtml(session.last_message || "No messages yet")}</span>
    `;
    container.appendChild(item);
  });
}

function renderHistory(messages) {
  const history = document.getElementById("chat-history");
  history.innerHTML = "";
  if (!messages.length) {
    history.innerHTML = '<p class="muted">Start a session and ask the first grounded question.</p>';
    return;
  }

  messages.forEach((message) => {
    const run = message.turn_id ? chatState.runsByTurnId[message.turn_id] : null;
    const article = document.createElement("article");
    article.className = `message-card ${message.role === "assistant" ? "assistant" : "user"} ${message.answer_status === "refused" ? "refusal" : ""}`.trim();
    article.innerHTML = `
      <div class="message-meta">
        <strong>${escapeHtml(message.role === "assistant" ? "Assistant" : "You")}</strong>
        <span class="muted">${escapeHtml(message.created_at)}</span>
      </div>
      <p>${escapeHtml(message.content)}</p>
      ${message.refusal_category ? `<span class="pill warning-pill">${escapeHtml(message.refusal_category)}</span>` : ""}
      ${
        run
          ? `
            <div class="message-meta-row">
              ${renderRunBadge(run)}
              <button type="button" class="secondary debug-history-button" data-run-id="${escapeHtml(run.run_id)}">Inspect Debug View</button>
            </div>
          `
          : ""
      }
    `;
    history.appendChild(article);
  });
  history.scrollTop = history.scrollHeight;
}

function renderDebug(payload) {
  chatState.latestPayload = payload || null;
  document.getElementById("debug-output").textContent = JSON.stringify(payload || {}, null, 2);
}

function renderRunBadge(run) {
  if (!run) {
    return "";
  }
  const toneClass =
    run.prompt_injection_result === "refused"
      ? "warning-pill"
      : run.prompt_injection_result === "clear"
        ? ""
        : "safety-pill";
  const label =
    run.prompt_injection_result === "clear"
      ? run.groundedness_status || "grounded"
      : `${run.prompt_injection_result} · risk ${Math.round(run.prompt_injection_risk_score || 0)}`;
  return `<span class="pill ${toneClass}">${escapeHtml(label)}</span>`;
}

function renderSafetySummary(payload) {
  const container = document.getElementById("safety-banner-container");
  container.innerHTML = "";
  if (!payload) {
    return;
  }

  const banners = [];
  if (payload.warning_summary) {
    banners.push({ tone: "warning", title: "Safety warning", body: payload.warning_summary });
  }
  if (payload.excluded_evidence_notice) {
    banners.push({ tone: "warning", title: "Excluded evidence", body: payload.excluded_evidence_notice });
  }
  if (payload.result_type === "refusal") {
    banners.push({
      tone: "warning",
      title: "Refusal reason",
      body: payload.refusal_reason || payload.refusal?.reason_category || "unsupported_request",
    });
  } else if (payload.groundedness_status) {
    banners.push({
      tone: payload.groundedness_status === "grounded" ? "info" : "warning",
      title: "Groundedness",
      body: payload.groundedness_status,
    });
  }
  if (!banners.length && payload.prompt_injection_result === "clear") {
    banners.push({ tone: "info", title: "Safety status", body: "No prompt-injection issues detected for this run." });
  }

  banners.forEach((banner) => {
    const article = document.createElement("article");
    article.className = `safety-banner ${banner.tone}`.trim();
    article.innerHTML = `
      <strong>${escapeHtml(banner.title)}</strong>
      <p>${escapeHtml(banner.body)}</p>
    `;
    container.appendChild(article);
  });
}

function updateRunControls(payload) {
  const runLabel = document.getElementById("run-label");
  const openButton = document.getElementById("open-debug-view");
  chatState.currentRunId = payload?.run_id || null;
  if (!payload?.run_id) {
    runLabel.textContent = "No completed run selected.";
    openButton.disabled = true;
    document.getElementById("refresh-debug-view").disabled = true;
    return;
  }
  runLabel.textContent = `Run ${payload.run_id} · ${payload.prompt_injection_result || "clear"} · ${payload.groundedness_status || "unknown"}`;
  openButton.disabled = false;
  document.getElementById("refresh-debug-view").disabled = false;
}

function renderCitationList(citations) {
  const panel = document.getElementById("citations-panel");
  panel.innerHTML = "";
  if (!citations || !citations.length) {
    panel.innerHTML = '<p class="muted">No citations for the current response.</p>';
    return;
  }
  const list = document.createElement("ol");
  list.className = "citation-list";
  citations.forEach((citation, index) => {
    const item = document.createElement("li");
    item.innerHTML = `
      <button type="button" class="citation-link" data-citation-id="${escapeHtml(citation.citation_id)}">
        [${index + 1}] ${escapeHtml(citation.document_title || citation.document_id)}
      </button>
      <span class="muted">${escapeHtml(citation.page_or_section || "no page / section")}</span>
    `;
    list.appendChild(item);
  });
  panel.appendChild(list);
}

function renderAnswerPayload(payload) {
  const panel = document.getElementById("answer-panel");
  panel.innerHTML = "";
  if (!payload) {
    panel.innerHTML = '<p class="muted">Ask a question to see a grounded answer or refusal.</p>';
    renderCitationList([]);
    renderSafetySummary(null);
    updateRunControls(null);
    renderDebug(null);
    return;
  }

  renderSafetySummary(payload);
  updateRunControls(payload);
  renderDebug(payload);
  if (payload.result_type === "refusal") {
    panel.innerHTML = `
      <div class="refusal-box">
        <h3>${escapeHtml(payload.refusal.refusal_text)}</h3>
        <p class="muted">Reason: ${escapeHtml(payload.refusal.reason_category)}</p>
        <p class="muted">Prompt-injection result: ${escapeHtml(payload.prompt_injection_result || "clear")}</p>
        <p class="muted">${escapeHtml(JSON.stringify(payload.refusal.supporting_metrics || {}))}</p>
      </div>
    `;
    renderCitationList([]);
    setAnswerStatus("Refused");
    return;
  }

  const citations = payload.citations || [];
  const markers = citations.map((citation, index) => {
    return `<button type="button" class="citation-marker" data-citation-id="${escapeHtml(citation.citation_id)}">[${index + 1}]</button>`;
  }).join(" ");
  panel.innerHTML = `
    <div class="answer-copy">
      <p>${escapeHtml(payload.answer.text)}</p>
      ${markers ? `<div class="inline-citations">${markers}</div>` : ""}
    </div>
  `;
  renderCitationList(citations);
  setAnswerStatus("Completed");
}

function runSummaryFromResponse(payload) {
  if (!payload?.run_id) {
    return null;
  }
  return {
    run_id: payload.run_id,
    turn_id: payload.turn_id,
    session_id: payload.session_id,
    result_type: payload.result_type,
    answer_text: payload.answer?.text || payload.refusal?.refusal_text || null,
    refusal_reason: payload.refusal_reason || payload.refusal?.reason_category || null,
    groundedness_status: payload.groundedness_status,
    prompt_injection_result: payload.prompt_injection_result,
    prompt_injection_risk_score: payload.prompt_injection_risk_score || 0,
    warning_summary: payload.warning_summary || null,
    excluded_evidence_notice: payload.excluded_evidence_notice || null,
    created_at: new Date().toISOString(),
  };
}

function applyCollectionOptions() {
  const select = document.getElementById("chat-collection");
  const pendingValue = select.dataset.pendingValue;
  select.innerHTML = '<option value="">All collections</option>';
  chatState.collections.forEach((collection) => {
    const option = document.createElement("option");
    option.value = collection.collection_id;
    option.textContent = collection.name;
    select.appendChild(option);
  });
  if (pendingValue != null) {
    select.value = pendingValue;
    delete select.dataset.pendingValue;
  }
}

async function loadCollections() {
  const payload = await apiFetch("/collections");
  chatState.collections = payload.items || [];
  applyCollectionOptions();
}

async function loadSessions() {
  const payload = await apiFetch("/chat/sessions");
  chatState.sessions = payload.items || [];
  renderSessionList();
}

async function loadSessionRuns(sessionId) {
  const payload = await apiFetch(`/chat/${sessionId}/runs`);
  chatState.runs = payload.items || [];
  chatState.runsById = {};
  chatState.runsByTurnId = {};
  chatState.runs.forEach((run) => {
    chatState.runsById[run.run_id] = run;
    chatState.runsByTurnId[run.turn_id] = run;
  });
}

function renderDebugList(items, renderer) {
  if (!items || !items.length) {
    return '<p class="muted">None</p>';
  }
  return `<div class="debug-card-list">${items.map(renderer).join("")}</div>`;
}

function renderDebugPayload(payload) {
  const container = document.getElementById("debug-view-content");
  if (!payload) {
    container.innerHTML = '<p class="muted">No debug run selected yet.</p>';
    document.getElementById("debug-run-subtitle").textContent = "Select a completed run to inspect the pipeline state.";
    renderDebug(null);
    return;
  }

  chatState.latestDebugPayload = payload;
  document.getElementById("debug-run-subtitle").textContent = `Run ${payload.run_id} for turn ${payload.turn_id}`;
  container.innerHTML = `
    <div class="metric-grid">
      <div class="metric-card">
        <span class="muted">Groundedness</span>
        <strong>${escapeHtml(payload.groundedness_status || "-")}</strong>
      </div>
      <div class="metric-card">
        <span class="muted">Answerability</span>
        <strong>${payload.answerability_flag ? "answerable" : "not answerable"}</strong>
      </div>
      <div class="metric-card">
        <span class="muted">Safety result</span>
        <strong>${escapeHtml(payload.prompt_injection_result || "clear")}</strong>
      </div>
      <div class="metric-card">
        <span class="muted">Risk score</span>
        <strong>${escapeHtml(String(Math.round(payload.prompt_injection_risk_score || 0)))}</strong>
      </div>
      <div class="metric-card">
        <span class="muted">Latency</span>
        <strong>${escapeHtml(String(payload.latency_ms ?? "-"))} ms</strong>
      </div>
      <div class="metric-card">
        <span class="muted">Token count</span>
        <strong>${escapeHtml(String(payload.token_count ?? "-"))}</strong>
      </div>
    </div>

    <div class="grid-two">
      <section class="debug-section">
        <h3>Query</h3>
        <div class="snippet-box">${escapeHtml(payload.original_query || "-")}</div>
        <p class="muted">Mode: ${escapeHtml(payload.query_mode || "original")} · Retrieval: ${escapeHtml(payload.retrieval_mode || "-")}</p>
      </section>
      <section class="debug-section">
        <h3>Final decision</h3>
        <div class="snippet-box">${escapeHtml(payload.final_answer_or_refusal?.answer_text || payload.final_answer_or_refusal?.refusal_text || "-")}</div>
        <p class="muted">Warning summary: ${escapeHtml(payload.warning_summary || "none")}</p>
      </section>
    </div>

    <section class="debug-section">
      <h3>Safety issues</h3>
      ${renderDebugList(payload.all_safety_issues, (issue) => `
        <article class="debug-card">
          <strong>${escapeHtml(issue.matched_pattern || issue.detection_method)}</strong>
          <p>${escapeHtml(issue.classifier_reason || "")}</p>
          <p class="muted">Scope: ${escapeHtml(issue.issue_scope)} · Risk: ${escapeHtml(String(Math.round(issue.risk_score || 0)))} · Action: ${escapeHtml(issue.final_action)}</p>
        </article>
      `)}
    </section>

    <section class="debug-section">
      <h3>Retrieved chunks</h3>
      ${renderDebugList(payload.all_retrieved_chunks, (chunk) => `
        <article class="debug-card">
          <strong>${escapeHtml(chunk.document_title || chunk.document_id || chunk.chunk_id)}</strong>
          <p>${escapeHtml(chunk.content_snippet || "")}</p>
          <p class="muted">Chunk: ${escapeHtml(chunk.chunk_id)} · Score: ${escapeHtml(String(chunk.retrieval_score ?? "-"))}</p>
        </article>
      `)}
    </section>

    <section class="debug-section">
      <h3>Selected context</h3>
      ${renderDebugList(payload.selected_context_chunks, (chunk) => `
        <article class="debug-card">
          <strong>${escapeHtml(chunk.document_title || chunk.document_id || chunk.chunk_id)}</strong>
          <p>${escapeHtml(chunk.content_snippet || chunk.full_text || "")}</p>
        </article>
      `)}
    </section>

    <section class="debug-section">
      <h3>Excluded chunks</h3>
      ${renderDebugList(payload.excluded_chunks_with_reasons, (chunk) => `
        <article class="debug-card warning">
          <strong>${escapeHtml(chunk.document_title || chunk.document_id || chunk.chunk_id)}</strong>
          <p>${escapeHtml(chunk.exclusion_reason || "suspicious content")}</p>
        </article>
      `)}
    </section>

    <section class="debug-section">
      <h3>Citations</h3>
      ${renderDebugList(payload.citations, (citation) => `
        <article class="debug-card">
          <strong>${escapeHtml(citation.document_title || citation.document_id)}</strong>
          <p>${escapeHtml(citation.content_snippet || "")}</p>
          <p class="muted">${escapeHtml(citation.page_or_section || "no page / section")}</p>
        </article>
      `)}
    </section>
  `;
  renderDebug(payload);
}

async function openDebugView(runId) {
  if (!runId) {
    return;
  }
  const payload = await apiFetch(`/runs/${runId}`);
  chatState.currentRunId = runId;
  renderDebugPayload(payload);
  document.getElementById("debug-panel").hidden = !document.getElementById("debug-toggle").checked;
}

async function selectSession(sessionId) {
  const payload = await apiFetch(`/chat/sessions/${sessionId}`);
  chatState.sessionId = sessionId;
  updateUrlSession(sessionId);
  window.sessionStorage.setItem(sessionStorageKey("last-session-id"), sessionId);
  await loadSessionRuns(sessionId);
  renderSessionList();
  renderHistory(payload.turns || []);
  if (chatState.runs.length) {
    const latestRunId = chatState.runs[0].run_id;
    try {
      const debugPayload = await apiFetch(`/runs/${latestRunId}`);
      renderAnswerPayload(debugPayload.response_payload || null);
      if (document.getElementById("debug-toggle").checked) {
        renderDebugPayload(debugPayload);
      }
    } catch (_error) {
      renderAnswerPayload(null);
    }
  } else {
    renderAnswerPayload(null);
    renderDebugPayload(null);
  }
}

async function createSession() {
  persistControls();
  const payload = await apiFetch("/chat/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      collection_id: document.getElementById("chat-collection").value || null,
      retrieval_mode: document.getElementById("retrieval-mode").value,
    }),
  });
  await loadSessions();
  await selectSession(payload.session_id);
  return payload;
}

async function ensureSession() {
  if (chatState.sessionId) {
    return chatState.sessionId;
  }
  const created = await createSession();
  return created.session_id;
}

function setCancelEnabled(enabled) {
  document.getElementById("cancel-turn").disabled = !enabled;
}

async function submitQuestionNonStream(question) {
  const sessionId = await ensureSession();
  setAnswerStatus("Generating");
  setCancelEnabled(false);
  const payload = await apiFetch(`/chat/sessions/${sessionId}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      collection_id: document.getElementById("chat-collection").value || null,
      retrieval_mode: document.getElementById("retrieval-mode").value,
    }),
  });
  chatState.currentTurnId = payload.turn_id;
  const summary = runSummaryFromResponse(payload);
  if (summary) {
    chatState.runsById[summary.run_id] = summary;
    chatState.runsByTurnId[summary.turn_id] = summary;
  }
  renderAnswerPayload(payload);
  if (payload.run_id && document.getElementById("debug-toggle").checked) {
    await openDebugView(payload.run_id);
  }
  await loadSessions();
  await selectSession(sessionId);
}

async function submitQuestionStream(question) {
  const sessionId = await ensureSession();
  setAnswerStatus("Retrieving");
  setCancelEnabled(true);
  chatState.partialAnswer = "";
  document.getElementById("answer-panel").innerHTML = '<p class="muted">Preparing streamed answer...</p>';
  document.getElementById("citations-panel").innerHTML = '<p class="muted">Citations will appear when the final answer is completed.</p>';

  const response = await fetch(`${API_BASE}/chat/sessions/${sessionId}/ask-stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      collection_id: document.getElementById("chat-collection").value || null,
      retrieval_mode: document.getElementById("retrieval-mode").value,
    }),
  });
  if (!response.ok) {
    throw new Error("Streaming request failed");
  }
  chatState.streamActive = true;
  chatState.streamReader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (chatState.streamActive) {
    const { value, done } = await chatState.streamReader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (!line.trim()) {
        continue;
      }
      const event = JSON.parse(line);
      if (event.event === "turn_created") {
        chatState.currentTurnId = event.turn_id;
      } else if (event.event === "retrieving") {
        setAnswerStatus("Retrieving");
      } else if (event.event === "safety_checked") {
        setAnswerStatus("Safety checked");
      } else if (event.event === "context_packed") {
        setAnswerStatus(`Packed ${event.chunk_count} chunks`);
      } else if (event.event === "answerability_checked") {
        setAnswerStatus("Groundedness checked");
      } else if (event.event === "generating") {
        setAnswerStatus("Generating");
      } else if (event.event === "answer_chunk") {
        chatState.partialAnswer += event.text;
        document.getElementById("answer-panel").innerHTML = `<div class="answer-copy"><p>${escapeHtml(chatState.partialAnswer)}</p></div>`;
      } else if (event.event === "cancelled") {
        chatState.streamActive = false;
        setAnswerStatus("Cancelled");
        setCancelEnabled(false);
        document.getElementById("answer-panel").innerHTML = '<div class="refusal-box"><h3>Generation cancelled.</h3></div>';
      } else if (event.event === "completed") {
        chatState.streamActive = false;
        setCancelEnabled(false);
        renderAnswerPayload(event);
        const summary = runSummaryFromResponse(event);
        if (summary) {
          chatState.runsById[summary.run_id] = summary;
          chatState.runsByTurnId[summary.turn_id] = summary;
        }
        if (event.run_id && document.getElementById("debug-toggle").checked) {
          await openDebugView(event.run_id);
        }
        await loadSessions();
        await selectSession(sessionId);
      }
      renderDebug(event);
    }
  }
}

async function handleQuestionSubmit(event) {
  event.preventDefault();
  const question = document.getElementById("question-input").value.trim();
  if (!question) {
    setChatStatus("Enter a question before sending.", "error");
    return;
  }
  persistControls();
  try {
    setChatStatus("Submitting question...");
    if (document.getElementById("stream-toggle").checked) {
      await submitQuestionStream(question);
    } else {
      await submitQuestionNonStream(question);
    }
    event.target.reset();
    restoreControls();
    setChatStatus("Question completed.", "success");
  } catch (error) {
    setChatStatus(error.message, "error");
    openChatError(error.message);
    setCancelEnabled(false);
  }
}

async function handleCancelTurn() {
  if (!chatState.sessionId || !chatState.currentTurnId) {
    return;
  }
  try {
    setChatStatus("Cancelling turn...");
    await apiFetch(`/chat/sessions/${chatState.sessionId}/turns/${chatState.currentTurnId}/cancel`, {
      method: "POST",
    });
    setAnswerStatus("Cancelling");
  } catch (error) {
    setChatStatus(error.message, "error");
    openChatError(error.message);
  }
}

async function openCitationModal(citationId) {
  if (!chatState.sessionId) {
    return;
  }
  try {
    const detail = await apiFetch(`/chat/sessions/${chatState.sessionId}/citations/${citationId}`);
    document.getElementById("citation-document-title").textContent = detail.document_title || detail.document_id;
    document.getElementById("citation-chunk-id").textContent = detail.chunk_id;
    document.getElementById("citation-page-section").textContent = detail.page_or_section || "-";
    document.getElementById("citation-retrieval-mode").textContent = detail.retrieval_mode || "-";
    document.getElementById("citation-score").textContent = detail.retrieval_score == null ? "-" : String(detail.retrieval_score);
    document.getElementById("citation-source-url").textContent = detail.source_url || "-";
    document.getElementById("citation-snippet").textContent = detail.full_snippet || detail.content_snippet || "";
    document.getElementById("citation-library-link").href = `./document-library.html?document_id=${encodeURIComponent(detail.document_id)}`;
    document.getElementById("citation-modal").classList.add("open");
  } catch (error) {
    setChatStatus(error.message, "error");
    openChatError(error.message);
  }
}

function closeCitationModal() {
  document.getElementById("citation-modal").classList.remove("open");
}

document.getElementById("chat-form").addEventListener("submit", (event) => {
  handleQuestionSubmit(event).catch((error) => {
    setChatStatus(error.message, "error");
    openChatError(error.message);
  });
});
document.getElementById("new-session").addEventListener("click", () => {
  createSession().catch((error) => {
    setChatStatus(error.message, "error");
    openChatError(error.message);
  });
});
document.getElementById("session-list").addEventListener("click", (event) => {
  const button = event.target.closest("button[data-session-id]");
  if (!button) {
    return;
  }
  selectSession(button.dataset.sessionId).catch((error) => {
    setChatStatus(error.message, "error");
    openChatError(error.message);
  });
});
document.getElementById("chat-history").addEventListener("click", (event) => {
  const button = event.target.closest("[data-run-id]");
  if (!button) {
    return;
  }
  document.getElementById("debug-toggle").checked = true;
  document.getElementById("debug-panel").hidden = false;
  openDebugView(button.dataset.runId).catch((error) => {
    setChatStatus(error.message, "error");
    openChatError(error.message);
  });
});
document.getElementById("cancel-turn").addEventListener("click", () => {
  handleCancelTurn().catch((error) => {
    setChatStatus(error.message, "error");
    openChatError(error.message);
  });
});
document.getElementById("open-debug-view").addEventListener("click", () => {
  if (!chatState.currentRunId) {
    return;
  }
  document.getElementById("debug-toggle").checked = true;
  document.getElementById("debug-panel").hidden = false;
  openDebugView(chatState.currentRunId).catch((error) => {
    setChatStatus(error.message, "error");
    openChatError(error.message);
  });
});
document.getElementById("refresh-debug-view").addEventListener("click", () => {
  if (!chatState.currentRunId) {
    return;
  }
  openDebugView(chatState.currentRunId).catch((error) => {
    setChatStatus(error.message, "error");
    openChatError(error.message);
  });
});
document.getElementById("citations-panel").addEventListener("click", (event) => {
  const target = event.target.closest("[data-citation-id]");
  if (!target) {
    return;
  }
  openCitationModal(target.dataset.citationId);
});
document.getElementById("answer-panel").addEventListener("click", (event) => {
  const target = event.target.closest("[data-citation-id]");
  if (!target) {
    return;
  }
  openCitationModal(target.dataset.citationId);
});
document.getElementById("citation-close").addEventListener("click", closeCitationModal);
document.getElementById("citation-modal").addEventListener("click", (event) => {
  if (event.target.id === "citation-modal") {
    closeCitationModal();
  }
});
document.getElementById("chat-error-close").addEventListener("click", closeChatError);
document.getElementById("chat-error-modal").addEventListener("click", (event) => {
  if (event.target.id === "chat-error-modal") {
    closeChatError();
  }
});
document.getElementById("chat-collection").addEventListener("change", persistControls);
document.getElementById("retrieval-mode").addEventListener("change", persistControls);
document.getElementById("stream-toggle").addEventListener("change", persistControls);
document.getElementById("debug-toggle").addEventListener("change", (event) => {
  document.getElementById("debug-panel").hidden = !event.target.checked;
  if (event.target.checked && chatState.currentRunId) {
    openDebugView(chatState.currentRunId).catch((error) => {
      setChatStatus(error.message, "error");
      openChatError(error.message);
    });
  }
  persistControls();
});

restoreControls();

Promise.all([loadCollections(), loadSessions()]).then(async () => {
  const preferredSessionId =
    currentQueryParam("session_id") ||
    window.sessionStorage.getItem(sessionStorageKey("last-session-id"));
  if (preferredSessionId) {
    try {
      await selectSession(preferredSessionId);
      window.sessionStorage.setItem(sessionStorageKey("last-session-id"), preferredSessionId);
      return;
    } catch (_error) {
      updateUrlSession(null);
    }
  }
  renderAnswerPayload(null);
  renderDebugPayload(null);
}).catch((error) => {
  setChatStatus(error.message, "error");
  openChatError(error.message);
});
