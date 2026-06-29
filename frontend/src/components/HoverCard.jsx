import React from "react";
import { createPortal } from "react-dom";

export default function HoverCard({ chunk, position }) {
  if (!chunk) return null;

  const score = chunk.similarity_score || chunk.score || 0;
  const title = chunk.title || chunk.metadata?.title || "Untitled";
  const text = chunk.text || chunk.content || chunk.metadata?.text || "";
  const excerpt = text.length > 150 ? text.slice(0, 150) + "..." : text;

  return createPortal(
    <div
      style={{
        position: "fixed",
        top: position.top,
        left: position.left,
        zIndex: 99999,
        maxWidth: "320px",
        backgroundColor: "#fff",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-md)",
        boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
        padding: "12px",
        fontSize: "13px",
        lineHeight: "1.5",
      }}
    >
      <div
        style={{
          fontWeight: "600",
          marginBottom: "4px",
          fontSize: "14px",
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
      >
        {title}
      </div>
      <div style={{ marginBottom: "8px" }}>
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "4px",
            fontSize: "11px",
            fontWeight: "500",
            color: "var(--accent-strong)",
            backgroundColor: "rgba(99, 102, 241, 0.08)",
            padding: "2px 6px",
            borderRadius: "var(--radius-sm)",
            border: "1px solid var(--border)",
          }}
        >
          {(score * 100).toFixed(1)}% relevance
        </span>
      </div>
      <div
        style={{
          fontSize: "12px",
          color: "var(--text-secondary)",
          lineHeight: "1.5",
        }}
      >
        {excerpt}
      </div>
    </div>,
    document.body
  );
}
