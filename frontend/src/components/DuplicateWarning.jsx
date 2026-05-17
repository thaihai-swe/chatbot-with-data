import { DUPLICATE_ACTIONS } from "../constants/statuses";

function DuplicateWarning({ attempt, onDecide }) {
  if (!attempt) {
    return null;
  }

  const evidence = attempt.duplicate_evidence_json
    ? JSON.parse(attempt.duplicate_evidence_json)
    : {};

  return (
    <section className="panel" style={{ border: "2px solid var(--warning)", background: "var(--warning-soft)" }} aria-live="polite">
      <div className="panel-heading">
        <div>
          <h2 style={{ color: "var(--warning)", display: "flex", alignItems: "center", gap: "10px" }}>
            <span>⚠️</span> Duplicate Decision Required
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>The system detected an existing document that may be a duplicate of your recent ingestion.</p>
        </div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "24px", marginBottom: "32px" }}>
        <div className="field">
          <span className="eyebrow">Match Type</span>
          <span style={{ fontWeight: "700", fontSize: "16px", textTransform: "capitalize" }}>{attempt.duplicate_status}</span>
        </div>
        <div className="field">
          <span className="eyebrow">Detection Logic</span>
          <span style={{ fontWeight: "700", fontSize: "16px" }}>{evidence.detection_method || "Heuristic Analysis"}</span>
        </div>
        {"similarity_score" in evidence && (
          <div className="field">
            <span className="eyebrow">Confidence</span>
            <span style={{ fontWeight: "700", fontSize: "16px" }}>{(evidence.similarity_score * 100).toFixed(1)}%</span>
          </div>
        )}
      </div>

      <div style={{ padding: "20px", background: "var(--surface)", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", marginBottom: "32px" }}>
        <span className="eyebrow" style={{ fontSize: "10px", marginBottom: "8px" }}>Conflict Context</span>
        <div style={{ fontSize: "14px", lineHeight: "1.5" }}>
          Ingestion attempt <span className="mono" style={{ background: "var(--surface-muted)", padding: "2px 6px", borderRadius: "4px" }}>{attempt.id.slice(0, 12)}...</span> 
          matches existing document <span className="mono" style={{ background: "var(--surface-muted)", padding: "2px 6px", borderRadius: "4px" }}>{attempt.duplicate_match_document_id?.slice(0, 12) || "unknown"}...</span>
        </div>
      </div>

      <div style={{ display: "flex", gap: "12px" }}>
        {DUPLICATE_ACTIONS.map((action) => (
          <button
            className={`button ${action.value === 'overwrite' || action.value === 'create_new' ? 'button-primary' : 'button-ghost'}`}
            style={{ 
              flex: 1, 
              background: action.value === 'ignore' ? 'var(--danger-soft)' : undefined,
              color: action.value === 'ignore' ? 'var(--danger)' : undefined,
              borderColor: action.value === 'ignore' ? 'var(--danger)' : undefined
            }}
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
