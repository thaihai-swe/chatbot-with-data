function FaithfulnessChip({ score }) {
  if (score === null || score === undefined) return null;

  const pct = Math.round(score * 100);
  const label = score >= 0.7 ? "High" : score >= 0.3 ? "Med" : "Low";
  const color = score >= 0.7 ? "var(--success)" : score >= 0.3 ? "var(--warning)" : "var(--danger)";

  return (
    <span
      className="faithfulness-chip"
      title={`${pct}% grounded`}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "4px",
        padding: "2px 8px",
        borderRadius: "var(--radius-md)",
        background: color,
        color: "#fff",
        fontSize: "11px",
        fontWeight: 700,
        cursor: "default",
      }}
      tabIndex={0}
      role="status"
      aria-label={`Groundedness: ${label}, ${pct} percent`}
    >
      <span>{label}</span>
    </span>
  );
}

export default FaithfulnessChip;
