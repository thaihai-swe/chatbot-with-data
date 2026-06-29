import React, { useState, useCallback } from "react";
import HoverCard from "./HoverCard";

export default function CitationBadge({ label, citation, chunk, onClick }) {
  const [hoverPos, setHoverPos] = useState(null);

  const handleMouseEnter = useCallback((e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const cardWidth = 320;
    const left = Math.max(4, Math.min(rect.left, window.innerWidth - cardWidth - 4));
    setHoverPos({ top: rect.bottom + 4, left });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setHoverPos(null);
  }, []);

  return (
    <span
      style={{
        cursor: "pointer",
        color: "var(--accent-strong)",
        fontWeight: "600",
        textDecoration: "underline",
        backgroundColor: "rgba(99, 102, 241, 0.08)",
        border: "1px solid var(--border)",
        padding: "2px 6px",
        borderRadius: "var(--radius-sm)",
        fontSize: "12px",
        margin: "0 2px",
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
    >
      [{label}]
      {hoverPos && chunk && <HoverCard chunk={chunk} position={hoverPos} />}
    </span>
  );
}
