import { useState } from "react";
import { generateProduct } from "../api/knowledgeApi";
import { useWorkspace } from "../context/WorkspaceContext";

const PRODUCT_TYPES = [
  { key: "study-guide", label: "Study Guide", emoji: "📘" },
  { key: "briefing-doc", label: "Briefing Doc", emoji: "📋" },
  { key: "faq", label: "FAQ", emoji: "❓" },
  { key: "timeline", label: "Timeline", emoji: "📅" },
  { key: "glossary", label: "Glossary", emoji: "📖" },
  { key: "flashcards", label: "Flashcards", emoji: "🃏" },
];

export default function StudioPanel() {
  const {
    selectedCollectionId,
    collectionName,
    generatedProducts,
    addGeneratedProduct,
    documents,
  } = useWorkspace();

  const [loading, setLoading] = useState(null);
  const [viewingIndex, setViewingIndex] = useState(null);
  const [activeTab, setActiveTab] = useState("active");

  const hasScope = !!selectedCollectionId;

  const handleGenerate = async (productType) => {
    if (!hasScope || loading) return;
    setLoading(productType);
    try {
      const result = await generateProduct(selectedCollectionId, productType);
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

  const activeDoc = documents && documents.length > 0 ? documents[0] : { title: "Q3_Product_Deck.pdf", size: "4.2 MB" };

  return (
    <div className="studio-panel" style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {!hasScope ? (
        <div className="studio-empty" style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "32px" }}>
          <span style={{ fontSize: "28px", marginBottom: "8px" }}>🎨</span>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", textAlign: "center" }}>
            Select a collection to generate knowledge products.
          </p>
        </div>
      ) : (
        <>
          <div className="studio-header" style={{ padding: "16px 20px", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border)" }}>
            <span style={{ fontSize: "14px", fontWeight: "800", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-primary)" }}>
              Knowledge Studio
            </span>
            <button className="button button-ghost" style={{ width: "24px", height: "24px", padding: 0 }} title="More Options">•••</button>
          </div>

          <div className="studio-tabs" style={{ display: "flex", gap: "4px", padding: "8px 12px", borderBottom: "1px solid var(--border)" }}>
            <button
              className={`button ${activeTab === "active" ? "button-primary" : "button-ghost"}`}
              style={{ flex: 1, height: "32px", fontSize: "12px", padding: 0 }}
              onClick={() => setActiveTab("active")}
            >
              Active View
            </button>
            <button
              className={`button ${activeTab === "history" ? "button-primary" : "button-ghost"}`}
              style={{ flex: 1, height: "32px", fontSize: "12px", padding: 0 }}
              onClick={() => setActiveTab("history")}
            >
              History ({generatedProducts.length})
            </button>
          </div>

          {activeTab === "active" && (
            <div style={{ display: "flex", flexDirection: "column", flex: 1, overflowY: "auto", padding: "16px", gap: "20px" }}>
              {/* SOURCE SECTION */}
              <div>
                <div style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.5px", color: "var(--text-secondary)", marginBottom: "8px" }}>
                  Source:
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "12px", background: "rgba(255, 255, 255, 0.03)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-lg)" }}>
                  <span style={{ fontSize: "24px" }}>📄</span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: "13px", fontWeight: "600", color: "var(--text-primary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {activeDoc.title || activeDoc.name || "Document"}
                    </div>
                    <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
                      {activeDoc.size || "Size: [Unknown]"}
                    </div>
                  </div>
                  <span className="status-badge status-success" style={{ height: "20px", fontSize: "10px" }}>Uploaded</span>
                </div>
              </div>

              {/* RAG WORKFLOW TIMELINE */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <span style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.5px", color: "var(--text-secondary)" }}>
                    RAG Workflow
                  </span>
                  <span style={{ fontSize: "11px", fontWeight: "600", color: "var(--accent)" }}>
                    Progress: 85%
                  </span>
                </div>
                {/* Visual Progress Stepper timeline */}
                <div style={{ display: "flex", gap: "4px", alignItems: "center", justifyContent: "space-between", padding: "8px 0" }}>
                  {[
                    { label: "Ingestion", icon: "📥" },
                    { label: "Vectorization", icon: "⚙️" },
                    { label: "Storage", icon: "💾" },
                    { label: "Retrieval", icon: "🔍" },
                    { label: "Generation", icon: "🎨" }
                  ].map((step, i) => (
                    <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "4px", flex: 1 }}>
                      <div style={{
                        width: "28px",
                        height: "28px",
                        borderRadius: "50%",
                        background: i < 4 ? "var(--gradient-primary)" : "var(--border)",
                        color: i < 4 ? "white" : "var(--text-secondary)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "12px",
                        boxShadow: i < 4 ? "0 2px 8px rgba(99, 91, 255, 0.25)" : "none"
                      }}>
                        {step.icon}
                      </div>
                      <span style={{ fontSize: "8px", textAlign: "center", color: "var(--text-secondary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", width: "100%" }}>
                        {step.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* MARKDOWN SUMMARY / GENERATOR */}
              <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: "200px" }}>
                <div style={{ fontSize: "11px", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.5px", color: "var(--text-secondary)", marginBottom: "8px" }}>
                  Markdown Summary
                </div>
                <div style={{ flex: 1, background: "rgba(255, 255, 255, 0.02)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-lg)", padding: "16px", overflowY: "auto" }}>
                  {viewedProduct ? (
                    <div>
                      <div style={{ fontSize: "14px", fontWeight: 750, color: "var(--text-primary)", marginBottom: "12px" }}># {viewedProduct.label}</div>
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
                      <span style={{ fontSize: "24px", marginBottom: "8px" }}>💡</span>
                      <p style={{ fontSize: "12px", margin: 0 }}>Select a product type in chat generator to output summary details.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* METADATA REGION FOOTER */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", padding: "12px", background: "rgba(255, 255, 255, 0.02)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-md)", fontSize: "11px" }}>
                <div><span style={{ color: "var(--text-secondary)" }}>Sources:</span> <strong style={{ color: "var(--text-primary)" }}>Lumina</strong></div>
                <div><span style={{ color: "var(--text-secondary)" }}>Author:</span> <strong style={{ color: "var(--text-primary)" }}>Author</strong></div>
                <div><span style={{ color: "var(--text-secondary)" }}>References:</span> <strong style={{ color: "var(--text-primary)" }}>Button</strong></div>
                <div><span style={{ color: "var(--text-secondary)" }}>Date:</span> <strong style={{ color: "var(--text-primary)" }}>20-08-2023</strong></div>
              </div>
            </div>
          )}

          {activeTab === "history" && (
            <div className="studio-history" style={{ flex: 1, display: "flex", flexDirection: "column", overflowY: "auto" }}>
              {generatedProducts.length === 0 ? (
                <p style={{ fontSize: "12px", color: "var(--text-secondary)", padding: "32px", textAlign: "center" }}>
                  No products generated yet.
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
                      className={`studio-history-item ${viewedProduct?.id === p.id ? "studio-history-item-active" : ""}`}
                      style={{
                        borderBottom: "1px solid var(--border)",
                        padding: "16px",
                        cursor: "pointer",
                        transition: "all 0.2s ease"
                      }}
                    >
                      <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                        <span style={{ fontSize: "20px" }}>
                          {PRODUCT_TYPES.find((pt) => pt.key === p.type)?.emoji || "📄"}
                        </span>
                        <div className="studio-history-item-info">
                          <div style={{ fontSize: "13px", fontWeight: "600", color: "var(--text-primary)" }}>{p.label}</div>
                          <div style={{ fontSize: "11px", color: "var(--text-secondary)", marginTop: "2px" }}>
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
    </div>
  );
}

function Flashcard({ question, answer }) {
  const [revealed, setRevealed] = useState(false);
  return (
    <div className="flashcard" onClick={() => setRevealed(!revealed)}>
      <div className="flashcard-question">{question}</div>
      {revealed && <div className="flashcard-answer">{answer}</div>}
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
        if (line.startsWith("# ")) return <h1 key={i}>{parseInline(line.slice(2))}</h1>;
        if (line.startsWith("## ")) return <h2 key={i}>{parseInline(line.slice(3))}</h2>;
        if (line.startsWith("### ")) return <h3 key={i}>{parseInline(line.slice(4))}</h3>;
        if (line.startsWith("- ")) return <li key={i} style={{ fontSize: "13px", margin: "2px 0" }}>{parseInline(line.slice(2))}</li>;
        if (line.trim() === "") return <br key={i} />;
        return <p key={i} style={{ fontSize: "13px", margin: "4px 0", lineHeight: "1.5" }}>{parseInline(line)}</p>;
      })}
    </div>
  );
}
