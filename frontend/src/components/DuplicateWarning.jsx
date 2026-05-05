import { DUPLICATE_ACTIONS } from "../constants/statuses";

function DuplicateWarning({ attempt, onDecide }) {
  if (!attempt) {
    return null;
  }

  const evidence = attempt.duplicate_evidence_json
    ? JSON.parse(attempt.duplicate_evidence_json)
    : {};

  return (
    <section className="panel panel-warning" aria-live="polite">
      <h2>Duplicate decision required</h2>
      <p>
        <strong>{attempt.duplicate_status}</strong> was detected for{" "}
        <span className="mono">{attempt.id}</span>.
      </p>
      <p>
        Matched document:{" "}
        <span className="mono">{attempt.duplicate_match_document_id || "unknown"}</span>
      </p>
      <p>
        Detection method: <strong>{evidence.detection_method || "unknown"}</strong>
      </p>
      {"similarity_score" in evidence ? (
        <p>Similarity score: {Number(evidence.similarity_score).toFixed(2)}</p>
      ) : null}
      <div className="action-row">
        {DUPLICATE_ACTIONS.map((action) => (
          <button
            className="button"
            key={action.value}
            type="button"
            onClick={() => onDecide(attempt.id, action.value)}
          >
            {action.label}
          </button>
        ))}
      </div>
    </section>
  );
}

export default DuplicateWarning;
