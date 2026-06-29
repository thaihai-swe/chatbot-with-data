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
  } = useWorkspace();

  const [loading, setLoading] = useState(null);
  const [viewingIndex, setViewingIndex] = useState(null);

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
    } catch (err) {
      alert(`Failed to generate ${productType}: ${err.message}`);
    } finally {
      setLoading(null);
    }
  };

  const viewedProduct =
    viewingIndex !== null ? generatedProducts[viewingIndex] : generatedProducts[0] || null;

  return (
    <div className="studio-panel">
      {!hasScope ? (
        <div className="studio-empty">
          <span style={{ fontSize: "28px", marginBottom: "8px" }}>🎨</span>
          <p style={{ fontSize: "13px", color: "var(--text-secondary)", textAlign: "center" }}>
            Select a collection to generate knowledge products.
          </p>
        </div>
      ) : (
        <>
          <div className="studio-header">
            <span style={{ fontSize: "12px", fontWeight: 600, color: "var(--text-secondary)" }}>
              Knowledge Studio
            </span>
            {collectionName && (
              <span className="studio-scope">{collectionName}</span>
            )}
          </div>

          <div className="studio-actions">
            {PRODUCT_TYPES.map((pt) => (
              <button
                key={pt.key}
                onClick={() => handleGenerate(pt.key)}
                disabled={loading !== null}
                className={`studio-action-btn ${loading === pt.key ? "studio-action-loading" : ""}`}
              >
                <span style={{ fontSize: "16px" }}>{pt.emoji}</span>
                <span className="studio-action-label">{pt.label}</span>
                {loading === pt.key && <span className="studio-spinner" />}
              </button>
            ))}
          </div>

          <div className="studio-divider" />

          <div className="studio-history">
            <div className="studio-history-header">
              <span style={{ fontSize: "11px", fontWeight: 600, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                History ({generatedProducts.length})
              </span>
            </div>
            {generatedProducts.length === 0 ? (
              <p style={{ fontSize: "12px", color: "var(--text-tertiary)", padding: "16px", textAlign: "center" }}>
                No products generated yet.
              </p>
            ) : (
              <div className="studio-history-list">
                {generatedProducts.map((p, idx) => (
                  <div
                    key={p.id}
                    onClick={() => setViewingIndex(idx)}
                    className={`studio-history-item ${viewedProduct?.id === p.id ? "studio-history-item-active" : ""}`}
                  >
                    <span style={{ fontSize: "14px" }}>
                      {PRODUCT_TYPES.find((pt) => pt.key === p.type)?.emoji || "📄"}
                    </span>
                    <div className="studio-history-item-info">
                      <div style={{ fontSize: "12px", fontWeight: 500 }}>{p.label}</div>
                      <div style={{ fontSize: "10px", color: "var(--text-tertiary)" }}>
                        {new Date(p.createdAt).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {viewedProduct && (
            <div className="studio-viewer">
              <div className="studio-viewer-header">
                <span style={{ fontSize: "12px", fontWeight: 600 }}>{viewedProduct.label}</span>
              </div>
              <div className="studio-viewer-content">
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
