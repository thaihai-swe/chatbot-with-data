import DuplicateWarning from "../../components/DuplicateWarning";

function DuplicateDecisionScreen({ attempts, onDecide }) {
  if (!attempts.length) {
    return (
      <section className="panel">
        <h2>Duplicate queue</h2>
        <p>No duplicate decisions are waiting right now.</p>
      </section>
    );
  }

  return (
    <section className="stack">
      {attempts.map((attempt) => (
        <DuplicateWarning key={attempt.id} attempt={attempt} onDecide={onDecide} />
      ))}
    </section>
  );
}

export default DuplicateDecisionScreen;
