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
    <div className="playground-screen">
      <div className="playground-header">
        <h2>Strategy Comparison Playground</h2>
        <p>Compare how different retrieval configurations affect the final answer side-by-side.</p>
        
        <form onSubmit={runComparison} className="playground-form">
          <input 
            type="text" 
            className="input playground-input" 
            placeholder="Enter a query to compare strategies..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={isRunning}
          />
          <button type="submit" className="button" disabled={isRunning || !query.trim()}>
            {isRunning ? "Running..." : "Run Comparison"}
          </button>
        </form>
      </div>

      <div className="playground-grid">
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
