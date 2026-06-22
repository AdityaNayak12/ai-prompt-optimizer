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

  const { tokens_before, tokens_after, processing_time_ms } = response.metrics;
  const tokenDiff = tokens_after - tokens_before;
  const tokenPctChange = tokens_before > 0 ? Math.round((tokenDiff / tokens_before) * 100) : 0;

  return (
    <div className="card-response">
      {/* Performance Metrics */}
      <div className="metrics-row">
        <div className="metric-tag">
          Latency: <span className="metric-value">{processing_time_ms}ms</span>
        </div>
        <div className="metric-tag">
          Before: <span className="metric-value">{tokens_before} tok</span>
        </div>
        <div className="metric-tag">
          After: <span className="metric-value">{tokens_after} tok</span>
        </div>
        <div 
          className="metric-tag"
          style={{
            borderColor: tokenPctChange > 0 ? "rgba(124, 58, 237, 0.3)" : "rgba(16, 185, 129, 0.3)",
            backgroundColor: tokenPctChange > 0 ? "rgba(124, 58, 237, 0.05)" : "rgba(16, 185, 129, 0.05)",
          }}
        >
          Delta:{" "}
          <span 
            className="metric-value"
            style={{ color: tokenPctChange > 0 ? "#c084fc" : "#34d399" }}
          >
            {tokenPctChange > 0 ? `+${tokenPctChange}%` : `${tokenPctChange}%`}
          </span>
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
