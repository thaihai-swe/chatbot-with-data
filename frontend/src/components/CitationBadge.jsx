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

  const accentColor = "#00d992"; // Electric green

  return (
    <span
      style={{
        cursor: isValid ? "pointer" : "default",
        color: isValid ? accentColor : "var(--text-secondary)",
        fontWeight: "700",
        textDecoration: "none",
        backgroundColor: isValid ? "rgba(0, 217, 146, 0.08)" : "rgba(255, 255, 255, 0.02)",
        border: `1px solid ${isValid ? "rgba(0, 217, 146, 0.25)" : "var(--border)"}`,
        padding: "1px 6px",
        borderRadius: "var(--radius-sm)",
        fontSize: "11px",
        margin: "0 3px",
        opacity: isValid ? 1 : 0.6,
        display: "inline-flex",
        alignItems: "center"
      }}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={isValid ? onClick : undefined}
    >
      {label}
      {hoverPos && chunk && <HoverCard chunk={chunk} position={hoverPos} />}
    </span>
  );
}
