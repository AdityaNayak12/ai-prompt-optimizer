import { components } from "../types/api";

export type OptimizeRequest = components["schemas"]["OptimizeRequest"];
export type OptimizeResponse = components["schemas"]["OptimizeResponse"];
export type DetailResponse = components["schemas"]["DetailResponse"];
export type OptimizeMetrics = components["schemas"]["OptimizeMetrics"];

const BASE_URL = "http://127.0.0.1:8000/api/v1";

/**
 * Optimizes a prompt by sending it to the FastAPI backend.
 * Uses the auto-generated contract schemas for strict type safety.
 */
export async function optimizePrompt(data: OptimizeRequest): Promise<OptimizeResponse> {
  const response = await fetch(`${BASE_URL}/optimize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    let errorMsg = `API Request failed with status ${response.status}`;
    try {
      const errJson = (await response.json()) as DetailResponse;
      if (errJson.detail) {
        errorMsg = errJson.detail;
      }
    } catch {
      // Fallback if response is not JSON
    }
    throw new Error(errorMsg);
  }

  return (await response.json()) as OptimizeResponse;
}
