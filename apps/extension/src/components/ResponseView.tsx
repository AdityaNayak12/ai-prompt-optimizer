  import { OptimizeResponse } from "../utils/api-client";

interface ResponseViewProps {
  response: OptimizeResponse;
  onCopy: () => void;
}

export default function ResponseView({ response, onCopy }: ResponseViewProps) {
  const handleCopy = () => {
    navigator.clipboard.writeText(response.optimized_prompt);
    onCopy();
  };

  // Safe and lightweight renderer for markdown bullet points
  const renderExplanation = (text: string) => {
    const lines = text.split("\n");
    const listItems = lines
      .map((line) => line.trim())
      .filter((line) => line.startsWith("-") || line.startsWith("*") || /^\d+\./.test(line))
      .map((line, idx) => {
        // Strip the list marker (- or * or 1.)
        const content = line.replace(/^[-*\d\.]+\s+/, "").trim();
        return <li key={idx}>{content}</li>;
      });

    if (listItems.length === 0) {
      return <p style={{ whiteSpace: "pre-line" }}>{text}</p>;
    }

    return <ul>{listItems}</ul>;
  };

  const result = response.optimizationResult || {
    originalTokens: response.metrics.tokens_before,
    optimizedTokens: response.metrics.tokens_after,
    status: "Accepted",
    reason: null,
    recommendation: "Use Optimized Prompt",
    optimizationAccepted: true,
  };

  const isAccepted = result.optimizationAccepted;

  return (
    <div className="card-response">
      {/* Optimization Result Card */}
      <div 
        style={{
          borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
          paddingBottom: "1rem",
          marginBottom: "1rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.5rem"
        }}
      >
        <span className="form-label" style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", opacity: 0.8 }}>
          Optimization Result
        </span>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", fontSize: "0.85rem", color: "#9ca3af" }}>
          <div>
            Original: <span style={{ color: "#f3f4f6", fontWeight: "600" }}>{result.originalTokens} tokens</span>
          </div>
          <div>
            Optimized: <span style={{ color: "#f3f4f6", fontWeight: "600" }}>{result.optimizedTokens} tokens</span>
          </div>
        </div>

        <div style={{ marginTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.4rem", fontSize: "0.85rem" }}>
          <div>
            <span style={{ color: "#9ca3af" }}>Status:</span>{" "}
            <span 
              style={{ 
                fontWeight: "700", 
                color: isAccepted ? "#10b981" : "#ef4444",
                backgroundColor: isAccepted ? "rgba(16, 185, 129, 0.1)" : "rgba(239, 68, 68, 0.1)",
                padding: "0.2rem 0.5rem",
                borderRadius: "0.25rem",
                display: "inline-block"
              }}
            >
              {isAccepted ? "✅ Accepted" : "❌ Rejected"}
            </span>
          </div>
          
          {result.reason && (
            <div>
              <span style={{ color: "#9ca3af" }}>Reason:</span>{" "}
              <span style={{ color: "#f87171", fontWeight: "500" }}>{result.reason}</span>
            </div>
          )}

          <div>
            <span style={{ color: "#9ca3af" }}>Recommendation:</span>{" "}
            <span style={{ color: isAccepted ? "#60a5fa" : "#fbbf24", fontWeight: "600" }}>
              {result.recommendation}
            </span>
          </div>
        </div>
      </div>

      {/* Output Display */}
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span className="form-label" style={{ fontSize: "0.75rem" }}>Optimized Prompt</span>
        </div>
        <div className="optimized-box">{response.optimized_prompt}</div>
        <div className="card-actions">
          <button className="btn-secondary" onClick={handleCopy}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
            </svg>
            Copy Prompt
          </button>
        </div>
      </div>

      {/* Explanations Section */}
      <div className="explanation-section">
        <h3>Optimizations Made</h3>
        <div className="explanation-content">
          {renderExplanation(response.explanation)}
        </div>
      </div>
    </div>
  );
}
