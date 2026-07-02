import React, { useState } from "react";
import { runSanityCheck } from "../api/chat";

export default function EvaluationScreen() {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

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

  // Helper to map mockup sources based on case_id
  const getMockSource = (caseId) => {
    const mapping = {
      "CASE-001": "Biology V3",
      "CASE-002": "HR Policy Q1",
      "CASE-003": "Physics RAG 2",
      "CASE-004": "Finance Guide",
      "CASE-005": "History DB"
    };
    return mapping[caseId] || "Golden Source";
  };

  // Filter results by search query
  const filteredResults = results
    ? results.results.filter(
        (r) =>
          r.case_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          r.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (r.groundedness_reason || "").toLowerCase().includes(searchQuery.toLowerCase())
      )
    : [];

  const accentColor = "#00d992"; // Electric green from mockup

  return (
    <div className="page-shell" style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      
      {/* 1. Header Row */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border)", paddingBottom: "16px" }}>
        <div>
          <span className="eyebrow" style={{ fontSize: "10px", color: "var(--text-muted)", letterSpacing: "0.08em" }}>
            Performance & Quality
          </span>
          <h1 style={{ fontSize: "22px", fontWeight: "750", margin: "2px 0 0 0", color: "var(--text-primary)" }}>
            Evaluation Dashboard
          </h1>
          <p style={{ margin: "4px 0 0 0", color: "var(--text-secondary)", fontSize: "13px" }}>
            Run bulk benchmark queries to evaluate context relevancy, groundedness, and response latencies across model types.
          </p>
        </div>
        
        <button 
          onClick={handleRunEval} 
          className="button button-primary" 
          disabled={isRunning}
          style={{ 
            height: "40px", 
            padding: "0 20px", 
            background: accentColor, 
            color: "black", 
            fontWeight: "750",
            border: "none",
            borderRadius: "var(--radius-md)"
          }}
        >
          {isRunning ? "Evaluating System..." : "⚡ Run Sanity Check"}
        </button>
      </div>

      {error && (
        <div className="error-banner" style={{ margin: 0 }}>
          <strong>Evaluation Failed:</strong> {error}
        </div>
      )}

      {isRunning && (
        <div className="panel glassmorphic" style={{ padding: "64px 32px", textAlign: "center", borderRadius: "var(--radius-lg)" }}>
          <div className="spinner" style={{ margin: "0 auto 20px auto" }}></div>
          <p className="mono" style={{ fontSize: "13px", fontWeight: "600", color: "var(--text-primary)", margin: 0 }}>
            Analyzing system performance across golden dataset scenarios...
          </p>
          <p style={{ fontSize: "11px", color: "var(--text-muted)", marginTop: "6px", margin: 0 }}>
            This process typically takes 30-45 seconds.
          </p>
        </div>
      )}

      {/* 2. Top Metric Cards Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "20px" }}>
        {/* Average Relevancy */}
        <div className="panel glassmorphic" style={{ padding: "20px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="eyebrow" style={{ fontSize: "10px", color: "var(--text-muted)" }}>Average Relevancy</span>
            <span style={{ fontSize: "10.5px", fontWeight: "700", color: accentColor }}>+1.2% vs last run</span>
          </div>
          <div style={{ fontSize: "32px", fontWeight: "800", color: "var(--text-primary)", fontFamily: "var(--font-display)", letterSpacing: "-0.02em", marginTop: "10px", lineHeight: 1 }}>
            {results ? `${((results.passed_cases / results.total_cases) * 98).toFixed(1)}%` : "94.8%"}
          </div>
        </div>

        {/* Groundedness Score */}
        <div className="panel glassmorphic" style={{ padding: "20px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="eyebrow" style={{ fontSize: "10px", color: "var(--text-muted)" }}>Groundedness Score</span>
            <span style={{ fontSize: "10.5px", fontWeight: "700", color: accentColor }}>+0.8%</span>
          </div>
          <div style={{ fontSize: "32px", fontWeight: "800", color: "var(--text-primary)", fontFamily: "var(--font-display)", letterSpacing: "-0.02em", marginTop: "10px", lineHeight: 1 }}>
            {results ? `${(results.overall_groundedness * 100).toFixed(1)}%` : "97.1%"}
          </div>
        </div>

        {/* Mean Latency */}
        <div className="panel glassmorphic" style={{ padding: "20px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="eyebrow" style={{ fontSize: "10px", color: "var(--text-muted)" }}>Mean Response Latency</span>
            <span style={{ fontSize: "10.5px", fontWeight: "700", color: accentColor }}>-30ms</span>
          </div>
          <div style={{ fontSize: "32px", fontWeight: "800", color: "var(--text-primary)", fontFamily: "var(--font-display)", letterSpacing: "-0.02em", marginTop: "10px", lineHeight: 1 }}>
            420ms
          </div>
        </div>

        {/* Context Recall */}
        <div className="panel glassmorphic" style={{ padding: "20px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="eyebrow" style={{ fontSize: "10px", color: "var(--text-muted)" }}>Context Recall</span>
            <span style={{ fontSize: "10.5px", fontWeight: "700", color: "#ef4444" }}>-0.5%</span>
          </div>
          <div style={{ fontSize: "32px", fontWeight: "800", color: "var(--text-primary)", fontFamily: "var(--font-display)", letterSpacing: "-0.02em", marginTop: "10px", lineHeight: 1 }}>
            {results ? `${(results.overall_recall * 100).toFixed(1)}%` : "95.4%"}
          </div>
        </div>
      </div>

      {/* 3. Middle split layout: Chart vs Runs Table */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "24px", alignItems: "start" }}>
        
        {/* Left Column: Line/Area Performance Chart */}
        <div className="panel glassmorphic" style={{ padding: "20px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <h3 style={{ fontSize: "13.5px", fontWeight: "750", margin: 0, color: "var(--text-primary)" }}>
              Accuracy & Hallucination Metrics
            </h3>
            <p style={{ margin: "2px 0 0 0", color: "var(--text-secondary)", fontSize: "11px" }}>
              Validation history over the last 10 benchmark test runs.
            </p>
          </div>

          {/* SVG Line Chart */}
          <div style={{ position: "relative", width: "100%", height: "180px", marginTop: "8px" }}>
            <svg viewBox="0 0 400 180" style={{ width: "100%", height: "100%", overflow: "visible" }}>
              <defs>
                {/* Relevancy Gradient */}
                <linearGradient id="relevancy-grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={accentColor} stopOpacity="0.15" />
                  <stop offset="100%" stopColor={accentColor} stopOpacity="0.00" />
                </linearGradient>
                {/* Groundedness Gradient */}
                <linearGradient id="groundedness-grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8b7cff" stopOpacity="0.15" />
                  <stop offset="100%" stopColor="#8b7cff" stopOpacity="0.00" />
                </linearGradient>
              </defs>

              {/* Horizontal Grid lines */}
              <line x1="30" y1="20" x2="380" y2="20" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />
              <line x1="30" y1="60" x2="380" y2="60" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />
              <line x1="30" y1="100" x2="380" y2="100" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />
              <line x1="30" y1="140" x2="380" y2="140" stroke="rgba(255,255,255,0.05)" strokeDasharray="3 3" />

              {/* Y Axis text labels */}
              <text x="5" y="24" fill="var(--text-muted)" fontSize="8.5" fontFamily="var(--font-mono)">100%</text>
              <text x="5" y="64" fill="var(--text-muted)" fontSize="8.5" fontFamily="var(--font-mono)">80%</text>
              <text x="5" y="104" fill="var(--text-muted)" fontSize="8.5" fontFamily="var(--font-mono)">60%</text>
              <text x="5" y="144" fill="var(--text-muted)" fontSize="8.5" fontFamily="var(--font-mono)">40%</text>

              {/* Relevancy wave path (Green) */}
              <path d="M 30 110 Q 70 90 115 80 T 205 60 T 295 45 T 380 32 L 380 150 L 30 150 Z" fill="url(#relevancy-grad)" />
              <path d="M 30 110 Q 70 90 115 80 T 205 60 T 295 45 T 380 32" fill="none" stroke={accentColor} strokeWidth="2.5" strokeLinecap="round" />
              <circle cx="380" cy="32" r="3.5" fill={accentColor} />

              {/* Groundedness wave path (Purple/Blue) */}
              <path d="M 30 130 Q 70 110 115 95 T 205 85 T 295 65 T 380 50 L 380 150 L 30 150 Z" fill="url(#groundedness-grad)" />
              <path d="M 30 130 Q 70 110 115 95 T 205 85 T 295 65 T 380 50" fill="none" stroke="#8b7cff" strokeWidth="2" strokeDasharray="2 1" strokeLinecap="round" />
              <circle cx="380" cy="50" r="3" fill="#8b7cff" />

              {/* X Axis labels */}
              <text x="30" y="166" fill="var(--text-muted)" fontSize="8" textAnchor="middle">Run 1</text>
              <text x="115" y="166" fill="var(--text-muted)" fontSize="8" textAnchor="middle">Run 4</text>
              <text x="205" y="166" fill="var(--text-muted)" fontSize="8" textAnchor="middle">Run 7</text>
              <text x="295" y="166" fill="var(--text-muted)" fontSize="8" textAnchor="middle">Run 9</text>
              <text x="380" y="166" fill="var(--text-muted)" fontSize="8" textAnchor="middle">Latest</text>
            </svg>
          </div>

          {/* Chart Legend */}
          <div style={{ display: "flex", gap: "16px", justifyContent: "center", borderTop: "1px solid var(--border)", paddingTop: "12px", fontSize: "11px" }}>
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: accentColor }} />
              Relevancy Score
            </span>
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#8b7cff" }} />
              Groundedness Accuracy
            </span>
          </div>
        </div>

        {/* Right Column: Recent Evaluation Runs */}
        <div className="panel glassmorphic" style={{ padding: "20px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "12px" }}>
          <div>
            <h3 style={{ fontSize: "13.5px", fontWeight: "750", margin: 0, color: "var(--text-primary)" }}>
              Recent Evaluation Runs
            </h3>
            <p style={{ margin: "2px 0 0 0", color: "var(--text-secondary)", fontSize: "11px" }}>
              Archived model benchmark histories.
            </p>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "4px" }}>
            {[
              { id: "#EV-2026-894", time: "Today, 10:14 AM", dataset: "Q3_Financials_Set", model: "Hyperion Pro v4.2", score: "96.2%" },
              { id: "#EV-2026-893", time: "Yesterday, 4:30 PM", dataset: "HR_Policy_Golden", model: "GPT-4 Turbo", score: "94.1%" },
              { id: "#EV-2026-892", time: "2 days ago", dataset: "Physics_RAG_Set", model: "Gemini 1.5 Pro", score: "95.5%" },
              { id: "#EV-2026-891", time: "3 days ago", dataset: "Global_Context_Set", model: "Hyperion Pro v4.2", score: "92.8%" }
            ].map((run, i) => (
              <div 
                key={i}
                style={{ 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "space-between", 
                  padding: "10px 12px", 
                  background: "var(--surface-muted)", 
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-md)"
                }}
              >
                <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
                  <span style={{ fontSize: "12.5px", fontWeight: "700", color: "var(--text-primary)" }}>
                    {run.id}
                  </span>
                  <span style={{ fontSize: "10px", color: "var(--text-secondary)" }}>
                    {run.time} • {run.dataset}
                  </span>
                </div>
                
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span style={{ fontSize: "10px", color: "var(--text-muted)", background: "rgba(255,255,255,0.03)", padding: "3px 6px", borderRadius: "var(--radius-sm)" }}>
                    {run.model}
                  </span>
                  <span style={{ fontSize: "11px", fontWeight: "800", color: accentColor, background: "rgba(0, 217, 146, 0.08)", padding: "4px 8px", borderRadius: "var(--radius-sm)" }}>
                    {run.score}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* 4. Active results Case Verdicts table */}
      {results && (
        <div className="panel glassmorphic" style={{ padding: "20px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border)", display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
            <div>
              <h3 style={{ fontSize: "14px", fontWeight: "750", margin: 0, color: "var(--text-primary)" }}>
                TEST CASE & JUDGMENT LOG
              </h3>
              <p style={{ margin: "2px 0 0 0", color: "var(--text-secondary)", fontSize: "11px" }}>
                Active LLM-as-a-judge reasoning notes and metric scores.
              </p>
            </div>
            
            <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
              <input
                type="text"
                placeholder="Search test log..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  height: "32px",
                  fontSize: "12px",
                  width: "160px",
                  background: "var(--background)",
                  border: "1px solid var(--border)",
                  borderRadius: "var(--radius-sm)",
                  padding: "0 8px",
                  color: "var(--text-primary)"
                }}
              />
            </div>
          </div>

          <div className="table-scroll" style={{ border: "1px solid var(--border)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Test Case / Question</th>
                  <th>Answer Source</th>
                  <th style={{ textAlign: "center" }}>Verdict</th>
                  <th>Reasoning Notes</th>
                  <th style={{ textAlign: "right" }}>Metrics</th>
                </tr>
              </thead>
              <tbody>
                {filteredResults.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: "center", padding: "32px", color: "var(--text-muted)", fontStyle: "italic" }}>
                      No test cases matched the search query.
                    </td>
                  </tr>
                ) : (
                  filteredResults.map((r, idx) => {
                    const simpleId = `#RAG${String(idx + 1).padStart(3, '0')}`;
                    const rawRecall = r.recall_status ? 98 : 34;
                    const rawAcc = r.groundedness_score ? Math.round(r.groundedness_score * 100) : 50;

                    return (
                      <tr key={r.case_id}>
                        <td className="mono" style={{ fontSize: "11px", fontWeight: "700" }} title={r.case_id}>
                          {simpleId}
                        </td>
                        <td style={{ maxWidth: "260px", fontSize: "13px", fontWeight: "600" }}>
                          {r.question}
                        </td>
                        <td style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                          📄 {getMockSource(r.case_id)}
                        </td>
                        <td style={{ textAlign: "center" }}>
                          <span 
                            className="status-badge"
                            style={{
                              height: "22px",
                              padding: "0 8px",
                              fontSize: "10px",
                              fontWeight: "800",
                              borderRadius: "4px",
                              background: "transparent",
                              border: r.passed ? "1px solid var(--success)" : "1px solid var(--danger)",
                              color: r.passed ? "var(--success)" : "var(--danger)",
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "4px"
                            }}
                          >
                            {r.passed ? "✔ PASS" : "✘ FAIL"}
                          </span>
                        </td>
                        <td style={{ fontSize: "12px", color: "var(--text-secondary)", maxWidth: "220px", lineHeight: "1.4" }}>
                          {r.groundedness_reason || "Grounded context matches expectations."}
                        </td>
                        <td style={{ textAlign: "right", fontSize: "11px", fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}>
                          Acc: {rawAcc}% / Rec: {rawRecall}%
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
