import React, { useState, useEffect } from "react";
import PromptForm from "./PromptForm";
import ResponseView from "./ResponseView";
import { optimizePrompt, OptimizeRequest, OptimizeResponse } from "../utils/api-client";

export default function AppLayout() {
  const [prompt, setPrompt] = useState("");
  const [tone, setTone] = useState("professional");
  const [detailLevel, setDetailLevel] = useState("balanced");
  const [targetAudience, setTargetAudience] = useState("");
  const [groqModel, setGroqModel] = useState("llama3-8b-8192");
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<OptimizeResponse | null>(null);
  
  const [backendStatus, setBackendStatus] = useState<"checking" | "connected" | "disconnected">("checking");
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  
  const isSidePanel = window.location.pathname.endsWith("sidepanel.html");

  // Load selection text if passed from background context menu
  useEffect(() => {
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      chrome.storage.local.get("pendingSelection", (data) => {
        if (data.pendingSelection) {
          setPrompt(data.pendingSelection);
          chrome.storage.local.remove("pendingSelection");
        }
      });
    }
  }, []);

  // Check backend server health on startup
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/health");
        if (res.ok) {
          setBackendStatus("connected");
        } else {
          setBackendStatus("disconnected");
        }
      } catch {
        setBackendStatus("disconnected");
      }
    };
    checkHealth();
  }, []);

  const triggerToast = (message: string) => {
    setToastMessage(message);
    setTimeout(() => setToastMessage(null), 2000);
  };

  const handleOptimize = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || prompt.length < 3) {
      setError("Prompt must be at least 3 characters long.");
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    const payload: OptimizeRequest = {
      prompt: prompt.trim(),
      tone: tone || null,
      detail_level: detailLevel || null,
      target_audience: targetAudience.trim() || null,
      groq_model: groqModel || null,
    };

    try {
      const result = await optimizePrompt(payload);
      setResponse(result);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred. Is the backend server running?");
    } finally {
      setLoading(false);
    }
  };

  const openSidePanel = async () => {
    if (typeof chrome !== "undefined" && chrome.windows && chrome.sidePanel) {
      try {
        const currentWindow = await chrome.windows.getCurrent();
        if (currentWindow.id !== undefined) {
          await chrome.sidePanel.open({ windowId: currentWindow.id });
          window.close(); // Close the popup
        }
      } catch (err) {
        console.error("Failed to open side panel:", err);
      }
    }
  };

  return (
    <div className="app-container">
      {/* Toast Notification */}
      <div className={`toast ${toastMessage ? "show" : ""}`}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 6L9 17l-5-5" />
        </svg>
        {toastMessage}
      </div>

      <header>
        <div className="logo-section">
          <div className="logo-badge">P</div>
          <h1>Prompt Advisor</h1>
          <span 
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: backendStatus === "connected" ? "#10b981" : backendStatus === "disconnected" ? "#ef4444" : "#f59e0b",
              marginLeft: 4,
              display: "inline-block"
            }} 
            title={backendStatus === "connected" ? "Backend connected" : backendStatus === "disconnected" ? "Backend offline" : "Checking health..."}
          />
        </div>
        
        <div className="actions-section">
          {!isSidePanel && (
            <button className="btn-icon" onClick={openSidePanel} title="Open in Side Panel">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M9 3v18" />
              </svg>
            </button>
          )}
        </div>
      </header>

      <main className="main-content">
        <PromptForm
          prompt={prompt}
          setPrompt={setPrompt}
          tone={tone}
          setTone={setTone}
          detailLevel={detailLevel}
          setDetailLevel={setDetailLevel}
          targetAudience={targetAudience}
          setTargetAudience={setTargetAudience}
          groqModel={groqModel}
          setGroqModel={setGroqModel}
          loading={loading}
          onSubmit={handleOptimize}
        />

        {error && (
          <div 
            style={{
              padding: "0.75rem 1rem",
              backgroundColor: "rgba(239, 68, 68, 0.1)",
              border: "1px solid rgba(239, 68, 68, 0.2)",
              borderRadius: "0.5rem",
              color: "#f87171",
              fontSize: "0.85rem",
              display: "flex",
              alignItems: "center",
              gap: "0.5rem",
              animation: "fadeIn 0.3s ease-out"
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {error}
          </div>
        )}

        {loading && (
          <div className="card-response">
            <div className="shimmer-container">
              <div className="shimmer-bar small"></div>
              <div className="shimmer-bar large"></div>
              <div className="shimmer-bar medium"></div>
              <div className="shimmer-bar small"></div>
            </div>
          </div>
        )}

        {response && (
          <ResponseView 
            response={response} 
            onCopy={() => triggerToast("Optimized prompt copied!")} 
          />
        )}
      </main>
    </div>
  );
}
