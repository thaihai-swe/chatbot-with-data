import React, { useState, useEffect } from "react";
import StatusBadge from "./StatusBadge";

function IngestionStepper({ status, createdAt }) {
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    if (status === "processing" || status === "submitted") {
      const interval = setInterval(() => {
        setNow(Date.now());
      }, 500);
      return () => clearInterval(interval);
    }
  }, [status]);

  const elapsedSec = (now - new Date(createdAt).getTime()) / 1000;

  const stages = [
    { name: "Submitted", key: "submitted" },
    { name: "Parsing", key: "parsing" },
    { name: "Chunking", key: "chunking" },
    { name: "Embedding", key: "embedding" },
    { name: "Ready", key: "ready" }
  ];

  let activeIndex = 0;
  let isFailed = status === "failed";
  let isComplete = status === "completed";

  if (isComplete) {
    activeIndex = 5;
  } else if (isFailed) {
    if (elapsedSec < 1.5) activeIndex = 1;
    else if (elapsedSec < 3.0) activeIndex = 2;
    else activeIndex = 3;
  } else if (status === "submitted") {
    activeIndex = 0;
  } else if (status === "processing") {
    if (elapsedSec < 1.5) activeIndex = 1;
    else if (elapsedSec < 3.0) activeIndex = 2;
    else activeIndex = 3;
  }

  return (
    <div className="ingestion-stepper" style={{ display: "flex", alignItems: "center", gap: "4px", width: "100%", maxWidth: "160px" }}>
      {stages.map((stage, idx) => {
        let stepClass = "pending";
        let titleText = `${stage.name} - Pending`;

        if (isComplete || idx < activeIndex) {
          stepClass = "done";
          titleText = `${stage.name} - Completed`;
        } else if (idx === activeIndex) {
          if (isFailed) {
            stepClass = "failed";
            titleText = `${stage.name} - Failed`;
          } else {
            stepClass = "active";
            titleText = `${stage.name} - Active`;
          }
        }

        return (
          <React.Fragment key={stage.key}>
            {idx > 0 && (
              <div 
                className={`stepper-line ${idx <= activeIndex ? (isComplete || idx < activeIndex ? "line-done" : "line-active") : "line-pending"}`}
                style={{ flex: 1, height: "2px", transition: "all 0.3s ease" }}
              />
            )}
            <div 
              className={`stepper-dot dot-${stepClass}`}
              title={titleText}
              style={{
                width: "12px",
                height: "12px",
                borderRadius: "50%",
                transition: "all 0.3s ease",
                cursor: "help"
              }}
            />
          </React.Fragment>
        );
      })}
    </div>
  );
}

function DocumentTable({
  collections,
  documents,
  onDelete,
  onReingest,
  onMove,
  onViewDocument,
}) {
  if (!documents.length) {
    return (
      <section className="panel glassmorphic">
        <div className="empty-state">
          <h3 style={{ fontSize: "20px", marginBottom: "12px", color: "var(--text-primary)" }}>No documents found</h3>
          <p style={{ color: "var(--text-secondary)", fontSize: "15px" }}>Upload a source above to populate your library.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="panel glassmorphic" style={{ padding: "0", overflow: "hidden" }}>
      <div style={{ padding: "32px 32px 0" }}>
        <h2 style={{ fontSize: "20px", marginBottom: "8px" }}>Library Inventory</h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "14px", marginBottom: "24px" }}>Manage and organize your indexed source documents.</p>
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Document Title</th>
              <th>Source</th>
              <th>Collection</th>
              <th>Status</th>
              <th style={{ textAlign: "right" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((document) => (
              <tr key={document.id}>
                <td style={{ fontWeight: "650", color: "var(--text-primary)" }}>{document.title}</td>
                <td className="mono" style={{ fontSize: "11px", opacity: 0.7 }}>{document.source_type.toUpperCase()}</td>
                <td style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
                  {(document.collections || []).map((collection) => collection.name).join(", ") ||
                    "None"}
                </td>
                <td>
                  {document.is_attempt ? (
                    <IngestionStepper status={document.latest_status} createdAt={document.created_at} />
                  ) : (
                    <StatusBadge status={document.latest_status || "completed"} />
                  )}
                </td>
                <td>
                  <div style={{ display: "flex", gap: "8px", justifyContent: "flex-end" }}>
                    {onViewDocument && (
                      <button
                        className="button button-ghost"
                        style={{ height: "32px", padding: "0 10px", fontSize: "12px" }}
                        type="button"
                        disabled={document.is_attempt}
                        onClick={() => onViewDocument(document.id)}
                      >
                        View
                      </button>
                    )}
                    <button
                      className="button button-ghost"
                      style={{ height: "32px", padding: "0 10px", fontSize: "12px" }}
                      type="button"
                      disabled={document.is_attempt}
                      onClick={() => onReingest(document)}
                    >
                      Re-ingest
                    </button>
                    <select
                      style={{ width: "160px", height: "32px", fontSize: "12px", padding: "0 8px" }}
                      aria-label={`Move ${document.title} to collection`}
                      defaultValue=""
                      disabled={document.is_attempt}
                      onChange={(event) => {
                        if (!event.target.value) {
                          return;
                        }
                        onMove(document, [event.target.value]);
                        event.target.value = "";
                      }}
                    >
                      <option value="">Move to collection</option>
                      {collections.map((collection) => (
                        <option key={collection.id} value={collection.id}>
                          {collection.name}
                        </option>
                      ))}
                    </select>
                    <button
                      className="button button-danger"
                      style={{ height: "32px", padding: "0 10px", fontSize: "12px" }}
                      type="button"
                      disabled={document.is_attempt}
                      onClick={() => onDelete(document.id)}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default DocumentTable;
