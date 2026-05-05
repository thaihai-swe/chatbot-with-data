import { STATUS_COPY } from "../constants/statuses";

function StatusBadge({ status }) {
  const definition = STATUS_COPY[status] || {
    label: status || "Unknown",
    tone: "muted",
    description: "No additional status details are available.",
  };

  return (
    <span
      className={`status-badge status-${definition.tone}`}
      title={definition.description}
    >
      <strong>{definition.label}</strong>
      <span className="status-help">{definition.description}</span>
    </span>
  );
}

export default StatusBadge;
