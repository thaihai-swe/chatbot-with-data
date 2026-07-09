import { useState, useEffect, useRef, useMemo } from "react";
import { generateProduct } from "../api/knowledgeApi";
import { getSettings, updateSettings } from "../api/settings";
import { useWorkspace } from "../context/WorkspaceContext";

const PRODUCT_TYPES = [
  { key: "study-guide", label: "Study Guide", emoji: "📘", color: "rgb(59, 130, 246)", border: "rgba(59, 130, 246, 0.4)", bg: "rgba(59, 130, 246, 0.05)" },
  { key: "faq", label: "FAQ", emoji: "❓", color: "rgb(245, 158, 11)", border: "rgba(245, 158, 11, 0.4)", bg: "rgba(245, 158, 11, 0.05)" },
  { key: "glossary", label: "Glossary", emoji: "📖", color: "rgb(16, 185, 129)", border: "rgba(16, 185, 129, 0.4)", bg: "rgba(16, 185, 129, 0.05)" },
  { key: "flashcards", label: "Flashcards", emoji: "🃏", color: "rgb(139, 92, 246)", border: "rgba(139, 92, 246, 0.4)", bg: "rgba(139, 92, 246, 0.05)" }
];

export default function StudioPanel() {
  const {
    selectedCollectionId,
    collectionName,
    generatedProducts,
    addGeneratedProduct,
    documents,
    activeDocumentId,
    setActiveDocument,
    activeTrace,
  } = useWorkspace();

  const [loading, setLoading] = useState(null);
  const [viewingIndex, setViewingIndex] = useState(null);
  const [activeTab, setActiveTab] = useState("active");
  const [activeMainTab, setActiveMainTab] = useState("analytics");
  const [alpha, setAlpha] = useState(0.75);
  const [retrievalMode, setRetrievalMode] = useState("hybrid");
  const isInitialMount = useRef(true);



  useEffect(() => {
    getSettings().then(data => {
      if (data?.retrieval) {
        setAlpha(data.retrieval.hybrid_weight ?? 0.75);
        setRetrievalMode(data.retrieval.retrieval_mode ?? "hybrid");
      }
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    const timer = setTimeout(() => {
      updateSettings({ retrieval: { hybrid_weight: alpha } }).catch(console.error);
    }, 500);
    return () => clearTimeout(timer);
  }, [alpha]);

  const hasScope = !!selectedCollectionId;

  const histogramBins = useMemo(() => {
    const rawBins = [0, 0, 0, 0, 0];
    if (activeTrace?.retrieval?.retrieved_chunks) {
      activeTrace.retrieval.retrieved_chunks.forEach(chunk => {
        const score = chunk.similarity_score || 0;
        if (score <= 0.2) rawBins[0]++;
        else if (score <= 0.4) rawBins[1]++;
        else if (score <= 0.6) rawBins[2]++;
        else if (score <= 0.8) rawBins[3]++;
        else rawBins[4]++;
      });
    }
    const max = Math.max(...rawBins, 1);
    return rawBins.map((count, i) => {
      const labels = ["0.0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1.0"];
      // Show at least 5% height so the bar isn't completely invisible if 0
      const h = count === 0 ? 5 : (count / max) * 100;
      return {
        height: `${h}%`,
        value: count.toString(),
        label: labels[i]
      };
    });
  }, [activeTrace]);

  const handleGenerate = async (productType) => {
    if (!hasScope || loading) return;
    setLoading(productType);
    try {
      const result = await generateProduct(selectedCollectionId, productType, activeDocumentId);
      const product = {
        id: `${productType}-${Date.now()}`,
        type: productType,
        label: PRODUCT_TYPES.find((p) => p.key === productType).label,
        content: result.content || result,
        createdAt: new Date().toISOString(),
      };
      addGeneratedProduct(product);
      setViewingIndex(0);
      setActiveTab("active");
    } catch (err) {
      alert(`Failed to generate ${productType}: ${err.message}`);
    } finally {
      setLoading(null);
    }
  };

  const viewedProduct =
    viewingIndex !== null ? generatedProducts[viewingIndex] : generatedProducts[0] || null;

  const activeDoc = documents.find(d => d.id === activeDocumentId) || documents[0] || null;

  const handleCopy = () => {
    if (!viewedProduct) return;
    const textToCopy = typeof viewedProduct.content === "string" 
      ? viewedProduct.content 
      : JSON.stringify(viewedProduct.content, null, 2);
    navigator.clipboard.writeText(textToCopy);
    alert("Copied to clipboard!");
  };

  const handleDownload = () => {
    if (!viewedProduct) return;
    const text = typeof viewedProduct.content === "string" 
      ? viewedProduct.content 
      : JSON.stringify(viewedProduct.content, null, 2);
    const blob = new Blob([text], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = window.document.createElement("a");
    a.href = url;
    a.download = `${viewedProduct.type}-${Date.now()}.md`;
    window.document.body.appendChild(a);
    a.click();
    window.document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleRegenerate = () => {
    if (!viewedProduct) return;
    handleGenerate(viewedProduct.type);
  };

  const accentColor = "#00d992"; // Electric green from mockup

  return (
    <div className="studio-panel" style={{ height: "100%", display: "flex", flexDirection: "column", background: "var(--surface)" }}>
      {!hasScope ? (
        <div className="studio-empty" style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "32px" }}>
          <span style={{ fontSize: "28px", marginBottom: "8px" }}>📊</span>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", textAlign: "center" }}>
            Select a collection to open Studio & Analytics.
          </p>
        </div>
      ) : (
        <>
          {/* Header */}
          <div className="studio-header" style={{ padding: "16px 20px 12px 20px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border)" }}>
            <span style={{ fontSize: "15px", fontWeight: "800", color: "var(--text-primary)", letterSpacing: "-0.025em" }}>
              Studio & Analytics
            </span>
            <span style={{ fontSize: "10px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.05em", color: accentColor, background: "rgba(0, 217, 146, 0.08)", padding: "4px 8px", borderRadius: "var(--radius-sm)" }}>
              {collectionName || "Active Library"}
            </span>
          </div>

          {/* Main Category Tabs: Analytics vs Studio */}
          <div style={{ display: "flex", gap: "2px", padding: "8px 12px", borderBottom: "1px solid var(--border)", background: "rgba(0,0,0,0.08)" }}>
            <button
              onClick={() => setActiveMainTab("analytics")}
              className={`button ${activeMainTab === "analytics" ? "button-primary" : "button-ghost"}`}
              style={{ flex: 1, height: "30px", fontSize: "11px", borderRadius: "var(--radius-sm)", padding: 0 }}
            >
              Analytics
            </button>
            <button
              onClick={() => setActiveMainTab("studio")}
              className={`button ${activeMainTab === "studio" ? "button-primary" : "button-ghost"}`}
              style={{ flex: 1, height: "30px", fontSize: "11px", borderRadius: "var(--radius-sm)", padding: 0 }}
            >
              Knowledge Studio
            </button>
          </div>

          {/* TAB 1: ANALYTICS WORKSPACE */}
          {activeMainTab === "analytics" && (
            <div style={{ display: "flex", flexDirection: "column", flex: 1, overflowY: "auto", padding: "20px", gap: "20px" }}>
              
              {/* 1. Hybrid Search Alpha Slider */}
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <span style={{ fontSize: "12px", fontWeight: "750", color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.02em" }}>
                  1. Hybrid Search Alpha
                </span>
                
                <div 
                  className="panel glassmorphic" 
                  style={{ 
                    padding: "16px", 
                    borderRadius: "var(--radius-md)", 
                    border: "1px solid var(--border)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "10px"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>Alpha Ratio</span>
                    <span style={{ fontSize: "12px", fontWeight: "800", color: accentColor }}>
                      Alpha: {alpha.toFixed(2)}
                    </span>
                  </div>
                  
                  <input
                    type="range"
                    min="0.00"
                    max="1.00"
                    step="0.05"
                    value={alpha}
                    disabled={retrievalMode !== "hybrid"}
                    onChange={(e) => setAlpha(parseFloat(e.target.value))}
                    style={{ width: "100%", height: "6px", accentColor: accentColor, opacity: retrievalMode !== "hybrid" ? 0.5 : 1, cursor: retrievalMode !== "hybrid" ? "not-allowed" : "pointer" }}
                  />

                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "10px", color: "var(--text-muted)" }}>
                    <span>0.00 (Keyword)</span>
                    <span>1.00 (Vector)</span>
                  </div>
                </div>
              </div>

              {/* 2. Vector Chunk Retrieval (Bar Chart) */}
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                <span style={{ fontSize: "12px", fontWeight: "750", color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.02em" }}>
                  2. Vector Chunk Retrieval
                </span>

                <div 
                  className="panel glassmorphic" 
                  style={{ 
                    padding: "16px", 
                    borderRadius: "var(--radius-md)", 
                    border: "1px solid var(--border)",
                    display: "flex",
                    flexDirection: "column",
                    gap: "12px"
                  }}
                >
                  {/* flex bar container */}
                  <div style={{ display: "flex", alignItems: "end", justifyContent: "space-between", height: "80px", padding: "0 8px 4px 8px", borderBottom: "1px solid var(--border)" }}>
                    {histogramBins.map((bar, i) => (
                      <div 
                        key={i} 
                        style={{ 
                          width: "30px", 
                          height: bar.height, 
                          background: `linear-gradient(180deg, ${accentColor}, rgba(0, 217, 146, 0.2))`,
                          borderRadius: "4px 4px 0 0",
                          position: "relative",
                          transition: "height 0.4s ease"
                        }}
                        title={`Score bin: ${bar.label} (${bar.value} chunks)`}
                      />
                    ))}
                  </div>
                  <div style={{ fontSize: "10px", color: "var(--text-secondary)", textAlign: "center", fontStyle: "italic", margin: 0 }}>
                    Query Relevance Score Range
                  </div>
                </div>
              </div>

            </div>
          )}

          {/* TAB 2: STUDIO WORKSPACE (Original asset generator screens) */}
          {activeMainTab === "studio" && (
            <>
              {/* Navigation Tabs (History vs Active) */}
              <div className="studio-tabs" style={{ display: "flex", gap: "4px", padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>
                <button
                  className={`button ${activeTab === "active" ? "button-primary" : "button-ghost"}`}
                  style={{ flex: 1, height: "30px", fontSize: "11px", padding: 0 }}
                  onClick={() => setActiveTab("active")}
                >
                  Active Asset
                </button>
                <button
                  className={`button ${activeTab === "history" ? "button-primary" : "button-ghost"}`}
                  style={{ flex: 1, height: "30px", fontSize: "11px", padding: 0 }}
                  onClick={() => setActiveTab("history")}
                >
                  Asset History ({generatedProducts.length})
                </button>
              </div>

              {activeTab === "active" && (
                <div style={{ display: "flex", flexDirection: "column", flex: 1, overflowY: "auto", padding: "16px", gap: "16px" }}>
                  {/* Document Selector */}
                  <div>
                    {documents.length > 0 ? (
                      <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
                        <span style={{ position: "absolute", left: "12px", fontSize: "14px", zIndex: 1, pointerEvents: "none" }}>📄</span>
                        <select
                          id="doc-focus-selector"
                          value={activeDocumentId || ""}
                          onChange={(e) => setActiveDocument(e.target.value || null)}
                          style={{
                            width: "100%",
                            background: "rgba(255, 255, 255, 0.03)",
                            border: "1px solid var(--border)",
                            color: "var(--text-primary)",
                            borderRadius: "var(--radius-md)",
                            padding: "8px 24px 8px 32px",
                            fontSize: "13px",
                            fontWeight: "600",
                            cursor: "pointer",
                            outline: "none",
                            appearance: "none"
                          }}
                        >
                          <option value="">All Documents in Collection</option>
                          {documents.map((doc) => (
                            <option key={doc.id} value={doc.id}>
                              {doc.title}
                            </option>
                          ))}
                        </select>
                      </div>
                    ) : (
                      <div style={{ fontSize: "11px", color: "var(--text-muted)", fontStyle: "italic" }}>
                        No documents inside this collection.
                      </div>
                    )}
                  </div>

                  {/* Generator buttons */}
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "8px" }}>
                    {PRODUCT_TYPES.map((pt) => {
                      const isCurrentLoading = loading === pt.key;
                      return (
                        <button
                          key={pt.key}
                          onClick={() => handleGenerate(pt.key)}
                          disabled={loading !== null}
                          style={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            gap: "6px",
                            padding: "10px 2px",
                            borderRadius: "var(--radius-md)",
                            border: `1px solid ${pt.border}`,
                            background: pt.bg,
                            cursor: "pointer"
                          }}
                          title={`Generate ${pt.label}`}
                        >
                          {isCurrentLoading ? (
                            <div className="spinner" style={{ width: "16px", height: "16px", borderWidth: "2px", borderColor: pt.color }} />
                          ) : (
                            <span style={{ fontSize: "18px", color: pt.color }}>{pt.emoji}</span>
                          )}
                          <span style={{ fontSize: "9px", fontWeight: "750", color: "var(--text-primary)", textAlign: "center" }}>{pt.label}</span>
                        </button>
                      );
                    })}
                  </div>

                  {/* Previewer canvas */}
                  <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: "200px" }}>
                    <div style={{ flex: 1, background: "var(--surface-muted)", border: "1px solid var(--border)", borderRadius: "var(--radius-md)", padding: "16px", overflowY: "auto", position: "relative" }}>
                      {viewedProduct && (
                        <div style={{ position: "absolute", top: "12px", right: "12px", display: "flex", gap: "6px", zIndex: 5 }}>
                          <button className="button button-ghost" style={{ padding: 0, width: "26px", height: "26px", minWidth: "26px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border)" }} onClick={handleCopy} title="Copy Content">📋</button>
                          <button className="button button-ghost" style={{ padding: 0, width: "26px", height: "26px", minWidth: "26px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border)" }} onClick={handleDownload} title="Download Markdown">💾</button>
                          <button className="button button-ghost" style={{ padding: 0, width: "26px", height: "26px", minWidth: "26px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border)" }} onClick={handleRegenerate} title="Regenerate">🔄</button>
                        </div>
                      )}

                      {viewedProduct ? (
                        <div style={{ paddingTop: viewedProduct ? "24px" : "0" }}>
                          <div style={{ fontSize: "14px", fontWeight: 800, color: "var(--text-primary)", marginBottom: "12px", borderBottom: "1px solid var(--border)", paddingBottom: "8px" }}>
                            {viewedProduct.label}
                          </div>
                          {viewedProduct.type === "flashcards" ? (
                            <div className="flashcards-list">
                              {(Array.isArray(viewedProduct.content) ? viewedProduct.content : []).map((card, i) => (
                                <Flashcard key={i} question={card.question} answer={card.answer} />
                              ))}
                            </div>
                          ) : (
                            <MarkdownContent content={typeof viewedProduct.content === "string" ? viewedProduct.content : ""} />
                          )}
                        </div>
                      ) : (
                        <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "var(--text-muted)", textAlign: "center" }}>
                          <span style={{ fontSize: "28px", marginBottom: "8px" }}>💡</span>
                          <p style={{ fontSize: "11px", maxWidth: "200px", margin: 0, lineHeight: "1.4", fontWeight: "600", color: "var(--text-secondary)" }}>
                            Select a tool above to generate study assets.
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "history" && (
                <div className="studio-history" style={{ flex: 1, display: "flex", flexDirection: "column", overflowY: "auto" }}>
                  {generatedProducts.length === 0 ? (
                    <p style={{ fontSize: "11px", color: "var(--text-secondary)", padding: "32px", textAlign: "center" }}>
                      No assets generated yet.
                    </p>
                  ) : (
                    <div className="studio-history-list">
                      {generatedProducts.map((p, idx) => (
                        <div
                          key={p.id}
                          onClick={() => {
                            setViewingIndex(idx);
                            setActiveTab("active");
                          }}
                          style={{
                            borderBottom: "1px solid var(--border)",
                            padding: "12px",
                            cursor: "pointer",
                            background: viewedProduct?.id === p.id ? "rgba(255, 255, 255, 0.04)" : "transparent"
                          }}
                        >
                          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                            <span style={{ fontSize: "16px" }}>
                              {PRODUCT_TYPES.find((pt) => pt.key === p.type)?.emoji || "📄"}
                            </span>
                            <div className="studio-history-item-info">
                              <div style={{ fontSize: "12.5px", fontWeight: "600", color: "var(--text-primary)" }}>{p.label}</div>
                              <div style={{ fontSize: "10px", color: "var(--text-muted)", marginTop: "2px" }}>
                                {new Date(p.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}

function Flashcard({ question, answer }) {
  const [flipped, setFlipped] = useState(false);
  return (
    <div 
      className="flashcard-container" 
      onClick={() => setFlipped(!flipped)}
      style={{
        perspective: "1000px",
        width: "100%",
        height: "120px",
        cursor: "pointer",
        marginBottom: "12px"
      }}
    >
      <div style={{
        position: "relative",
        width: "100%",
        height: "100%",
        transition: "transform 0.6s",
        transformStyle: "preserve-3d",
        transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
        borderRadius: "var(--radius-lg)",
        border: "1px solid var(--glass-border)",
        background: "var(--surface-raised)",
        boxShadow: "var(--glass-shadow)"
      }}>
        {/* Front Side */}
        <div style={{
          position: "absolute",
          inset: 0,
          backfaceVisibility: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "16px",
          textAlign: "center",
          fontWeight: "600",
          fontSize: "13px",
          color: "var(--text-primary)"
        }}>
          ❓ {question}
        </div>
        
        {/* Back Side */}
        <div style={{
          position: "absolute",
          inset: 0,
          backfaceVisibility: "hidden",
          transform: "rotateY(180deg)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "16px",
          textAlign: "center",
          background: "rgba(99, 102, 241, 0.08)",
          borderRadius: "var(--radius-lg)",
          fontWeight: "600",
          fontSize: "13px",
          color: "var(--accent-strong)"
        }}>
          💡 {answer}
        </div>
      </div>
    </div>
  );
}

function parseInline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

function MarkdownContent({ content }) {
  const lines = content.split("\n");
  return (
    <div className="markdown-body">
      {lines.map((line, i) => {
        if (line.startsWith("```")) return null;
        if (line.startsWith("# ")) return <h1 key={i} style={{ fontSize: "16px", margin: "8px 0" }}>{parseInline(line.slice(2))}</h1>;
        if (line.startsWith("## ")) return <h2 key={i} style={{ fontSize: "14px", margin: "6px 0" }}>{parseInline(line.slice(3))}</h2>;
        if (line.startsWith("### ")) return <h3 key={i} style={{ fontSize: "13px", margin: "4px 0" }}>{parseInline(line.slice(4))}</h3>;
        if (line.startsWith("- ")) return <li key={i} style={{ fontSize: "13px", margin: "2px 0" }}>{parseInline(line.slice(2))}</li>;
        if (line.trim() === "") return <br key={i} />;
        return <p key={i} style={{ fontSize: "13px", margin: "4px 0", lineHeight: "1.5" }}>{parseInline(line)}</p>;
      })}
    </div>
  );
}
