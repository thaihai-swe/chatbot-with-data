import React, { useState, useCallback } from "react";
import HoverCard from "./HoverCard";

export default function CitationBadge({ label, citation, chunk, onClick }) {
  const [hoverPos, setHoverPos] = useState(null);
  const isValid = !!(citation && chunk);

  const handleMouseEnter = useCallback((e) => {
    if (!isValid) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const cardWidth = 320;
    const left = Math.max(4, Math.min(rect.left, window.innerWidth - cardWidth - 4));
    setHoverPos({ top: rect.bottom + 4, left });
  }, [isValid]);

  const handleMouseLeave = useCallback(() => {
    setHoverPos(null);
  }, []);

  return (
    <span
      style={{
        cursor: isValid ? "pointer" : "default",
        color: isValid ? "var(--accent-strong)" : "var(--text-secondary)",
        fontWeight: "600",
        textDecoration: isValid ? "underline" : "none",
        backgroundColor: isValid ? "rgba(99, 102, 241, 0.08)" : "rgba(0, 0, 0, 0.04)",
        border: "1px solid var(--border)",
        padding: "2px 6px",
        borderRadius: "var(--radius-sm)",
        fontSize: "12px",
        margin: "0 2px",
        opacity: isValid ? 1 : 0.6,
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={isValid ? onClick : undefined}
    >
      [{label}]
      {hoverPos && chunk && <HoverCard chunk={chunk} position={hoverPos} />}
    </span>
  );
}
