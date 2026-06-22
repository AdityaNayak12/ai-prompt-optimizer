import React from "react";

interface PromptFormProps {
  prompt: string;
  setPrompt: (val: string) => void;
  tone: string;
  setTone: (val: string) => void;
  detailLevel: string;
  setDetailLevel: (val: string) => void;
  targetAudience: string;
  setTargetAudience: (val: string) => void;
  groqModel: string;
  setGroqModel: (val: string) => void;
  loading: boolean;
  onSubmit: (e: React.FormEvent) => void;
}

export default function PromptForm({
  prompt,
  setPrompt,
  tone,
  setTone,
  detailLevel,
  setDetailLevel,
  targetAudience,
  setTargetAudience,
  groqModel,
  setGroqModel,
  loading,
  onSubmit,
}: PromptFormProps) {
  const isSubmitDisabled = loading || prompt.trim().length < 3;

  return (
    <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div className="form-group">
        <label className="form-label" htmlFor="prompt-input">
          Enter Your Prompt
        </label>
        <textarea
          id="prompt-input"
          className="textarea-premium"
          placeholder="Paste or type the prompt you want to optimize (e.g., 'explain recursion')..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={loading}
        />
      </div>

      <div className="controls-grid">
        <div className="form-group">
          <label className="form-label" htmlFor="model-select">
            Optimizer Model
          </label>
          <select
            id="model-select"
            className="select-premium"
            value={groqModel}
            onChange={(e) => setGroqModel(e.target.value)}
            disabled={loading}
          >
            <option value="llama3-8b-8192">Llama 3 8B (Fast)</option>
            <option value="llama3-70b-8192">Llama 3 70B (Smart)</option>
            <option value="mixtral-8x7b-32768">Mixtral 8x7B (Complex)</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="tone-select">
            Desired Tone
          </label>
          <select
            id="tone-select"
            className="select-premium"
            value={tone}
            onChange={(e) => setTone(e.target.value)}
            disabled={loading}
          >
            <option value="professional">Professional</option>
            <option value="conversational">Conversational</option>
            <option value="academic">Academic</option>
            <option value="concise">Concise</option>
            <option value="creative">Creative</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="detail-select">
            Detail Level
          </label>
          <select
            id="detail-select"
            className="select-premium"
            value={detailLevel}
            onChange={(e) => setDetailLevel(e.target.value)}
            disabled={loading}
          >
            <option value="balanced">Balanced</option>
            <option value="concise">Concise</option>
            <option value="detailed">Detailed</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="audience-input">
            Target Audience
          </label>
          <input
            id="audience-input"
            type="text"
            className="input-premium"
            placeholder="e.g. Beginners, Devs, Execs (Optional)"
            value={targetAudience}
            onChange={(e) => setTargetAudience(e.target.value)}
            disabled={loading}
          />
        </div>
      </div>

      <button type="submit" className="btn-primary" disabled={isSubmitDisabled}>
        {loading ? (
          <>
            <svg
              style={{ animation: "loadingShimmer 2s linear infinite" }}
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <line x1="12" y1="2" x2="12" y2="6" />
              <line x1="12" y1="18" x2="12" y2="22" />
              <line x1="4.93" y1="4.93" x2="7.76" y2="7.76" />
              <line x1="16.24" y1="16.24" x2="19.07" y2="19.07" />
              <line x1="2" y1="12" x2="6" y2="12" />
              <line x1="18" y1="12" x2="22" y2="12" />
              <line x1="4.93" y1="19.07" x2="7.76" y2="16.24" />
              <line x1="16.24" y1="7.76" x2="19.07" y2="4.93" />
            </svg>
            Optimizing...
          </>
        ) : (
          <>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
            Optimize Prompt
          </>
        )}
      </button>
    </form>
  );
}
