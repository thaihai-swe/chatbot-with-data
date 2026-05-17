import { STATUS_COPY } from "../constants/statuses";

function StatusBadge({ status }) {
  const definition = STATUS_COPY[status] || {
    label: status || "Unknown",
    tone: "muted",
    description: "No details available.",
  };

  return (
    <span
      className={`status-badge status-${definition.tone}`}
      title={definition.description}
    >
      {definition.label}
    </span>
  );
}

export default StatusBadge;
