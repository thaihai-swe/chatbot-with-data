import React, { useState } from "react";
import { runSanityCheck } from "../api/chat";

export default function EvaluationScreen() {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleRunEval = async () => {
    setIsRunning(true);
    setResults(null);
    setError(null);
    try {
      const data = await runSanityCheck();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="stack">
      <div className="panel">
        <div className="panel-heading">
          <div>
            <h2>Basic Evaluation (Sanity Check)</h2>
            <p className="hero-copy" style={{ fontSize: "0.9rem" }}>
              Run the "Golden Dataset" of 10-20 core scenarios to verify the system's Groundedness and Retrieval Recall.
            </p>
          </div>
          <button 
            onClick={handleRunEval} 
            className="button" 
            disabled={isRunning}
          >
            {isRunning ? "Running LLM Evaluation..." : "Start Sanity Check"}
          </button>
        </div>

        {error && (
          <div className="panel panel-danger" style={{ marginTop: "20px" }}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {isRunning && (
          <div style={{ marginTop: "30px", textAlign: "center" }}>
            <div className="spinner" style={{ margin: "0 auto 20px" }}></div>
            <p className="mono">Executing test cases and scoring with LLM-as-a-judge...</p>
            <p style={{ fontSize: "0.8rem", opacity: 0.6 }}>This may take 30-60 seconds depending on model latency.</p>
          </div>
        )}

        {results && (
          <div style={{ marginTop: "30px" }}>
            <div className="grid" style={{ gridTemplateColumns: "repeat(4, 1fr)", marginBottom: "30px" }}>
              <div className="panel status-muted">
                <span className="eyebrow" style={{ fontSize: "0.6rem" }}>Total Cases</span>
                <div style={{ fontSize: "1.8rem", fontWeight: "bold" }}>{results.total_cases}</div>
              </div>
              <div className="panel status-success">
                <span className="eyebrow" style={{ fontSize: "0.6rem" }}>Passed</span>
                <div style={{ fontSize: "1.8rem", fontWeight: "bold" }}>{results.passed_cases}</div>
              </div>
              <div className="panel status-info">
                <span className="eyebrow" style={{ fontSize: "0.6rem" }}>Avg Recall</span>
                <div style={{ fontSize: "1.8rem", fontWeight: "bold" }}>{(results.overall_recall * 100).toFixed(0)}%</div>
              </div>
              <div className="panel status-warning">
                <span className="eyebrow" style={{ fontSize: "0.6rem" }}>Avg Groundedness</span>
                <div style={{ fontSize: "1.8rem", fontWeight: "bold" }}>{(results.overall_groundedness * 100).toFixed(0)}%</div>
              </div>
            </div>

            <div className="table-scroll">
              <table className="mono" style={{ fontSize: "0.8rem" }}>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Question</th>
                    <th>Recall</th>
                    <th>Groundedness</th>
                    <th>Latency</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {results.results.map((r) => (
                    <tr key={r.case_id}>
                      <td>{r.case_id}</td>
                      <td style={{ maxWidth: "300px" }}>
                        <div>{r.question}</div>
                        {r.groundedness_reason && (
                          <div style={{ fontSize: "0.7rem", opacity: 0.6, marginTop: "4px", fontStyle: "italic" }}>
                            Reason: {r.groundedness_reason}
                          </div>
                        )}
                      </td>
                      <td>
                        <span className={`text-${r.recall_status ? "success" : "danger"}`}>
                          {r.recall_status ? "YES" : "NO"}
                        </span>
                      </td>
                      <td>{(r.groundedness_score * 100).toFixed(0)}%</td>
                      <td>{r.latency_ms}ms</td>
                      <td>
                        <span className={`status-badge ${r.passed ? "status-success" : "status-danger"}`} style={{ minWidth: "80px", textAlign: "center" }}>
                          {r.passed ? "PASS" : "FAIL"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
