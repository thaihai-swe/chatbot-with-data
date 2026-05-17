import React, { useState, useEffect } from "react";
import PlaygroundPanel from "../components/PlaygroundPanel";
import { createChatSession, streamChatTurn } from "../api/chat";

export default function PlaygroundScreen() {
  const [query, setQuery] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  const [panelAConfig, setPanelAConfig] = useState({
    retrieval_mode: "semantic",
    enable_hyde: false,
    enable_expansion: false,
    enable_reranking: true,
    enable_parent_child: true,
  });

  const [panelBConfig, setPanelBConfig] = useState({
    retrieval_mode: "hybrid",
    enable_hyde: true,
    enable_expansion: true,
    enable_reranking: true,
    enable_parent_child: true,
  });

  const [panelAResult, setPanelAResult] = useState(null);
  const [panelBResult, setPanelBResult] = useState(null);
  const [panelALoading, setPanelALoading] = useState(false);
  const [panelBLoading, setPanelBLoading] = useState(false);

  const runComparison = async (e) => {
    e.preventDefault();
    if (!query.trim() || isRunning) return;

    setIsRunning(true);
    setPanelALoading(true);
    setPanelBLoading(true);
    setPanelAResult({ answer: "", chunks: [] });
    setPanelBResult({ answer: "", chunks: [] });

    try {
      // Create a temporary session for both calls
      const session = await createChatSession([]);
      const sessionId = session.id;

      // Execute both in parallel
      await Promise.all([
        executeStrategy(sessionId, query, panelAConfig, setPanelAResult, setPanelALoading),
        executeStrategy(sessionId, query, panelBConfig, setPanelBResult, setPanelBLoading)
      ]);
    } catch (err) {
      console.error("Playground error:", err);
    } finally {
      setIsRunning(false);
    }
  };

  const executeStrategy = (sid, text, config, setResult, setLoading) => {
    return new Promise((resolve) => {
      let fullAnswer = "";
      streamChatTurn(sid, text, config, {
        onToken: (token) => {
          fullAnswer += token;
          setResult(prev => ({ ...prev, answer: fullAnswer }));
        },
        onCitations: (data) => {
          setResult(prev => ({ ...prev, chunks: data.retrieved_chunks || [] }));
        },
        onError: (err) => {
          setResult(prev => ({ ...prev, answer: `Error: ${err.message}` }));
          setLoading(false);
          resolve();
        },
        onDone: () => {
          setLoading(false);
          resolve();
        }
      });
    });
  };

  return (
    <div className="page-shell">
      <div className="hero">
        <div>
          <span className="eyebrow">A/B Analysis</span>
          <h1>Strategy Comparison</h1>
          <p className="hero-copy">Compare how different retrieval configurations and processing steps affect the final assistant response side-by-side.</p>
        </div>
      </div>

      <div className="panel" style={{ border: "1px solid var(--accent)", background: "var(--accent-soft)" }}>
        <form onSubmit={runComparison} style={{ display: "flex", gap: "16px", alignItems: "flex-end" }}>
          <div className="field" style={{ flex: 1, marginBottom: 0 }}>
            <label htmlFor="playground-query">Comparative Query</label>
            <input 
              id="playground-query"
              type="text" 
              placeholder="Enter a complex query to test retrieval logic..." 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={isRunning}
              style={{ background: "var(--surface)" }}
            />
          </div>
          <button 
            type="submit" 
            className="button button-primary" 
            disabled={isRunning || !query.trim()}
            style={{ height: "44px", padding: "0 32px" }}
          >
            {isRunning ? "Synthesizing..." : "Run Side-by-Side"}
          </button>
        </form>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "1fr 1fr", alignItems: "stretch" }}>
        <PlaygroundPanel 
          panelId="A" 
          config={panelAConfig} 
          onConfigChange={setPanelAConfig}
          result={panelAResult}
          isLoading={panelALoading}
          otherPanelChunks={panelBResult?.chunks || []}
        />
        <PlaygroundPanel 
          panelId="B" 
          config={panelBConfig} 
          onConfigChange={setPanelBConfig}
          result={panelBResult}
          isLoading={panelBLoading}
          otherPanelChunks={panelAResult?.chunks || []}
        />
      </div>
    </div>
  );
}
