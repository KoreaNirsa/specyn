import axios from "axios";

import { HealthResponse, SpecDocument, SpecRunResponse, SpecRunStreamEvent } from "../types";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8180";
const AI_SERVER_URL = import.meta.env.VITE_AI_SERVER_URL ?? "http://localhost:8100";
const SAMPLE_BACKEND_URL = import.meta.env.VITE_SAMPLE_BACKEND_URL ?? "http://localhost:8080";
const SAMPLE_AI_SERVER_URL = import.meta.env.VITE_SAMPLE_AI_SERVER_URL ?? "http://localhost:8000";

const backendClient = axios.create({
  baseURL: BACKEND_URL,
  timeout: 30000,
});

const aiServerClient = axios.create({
  baseURL: AI_SERVER_URL,
  timeout: 30000,
});

const sampleBackendClient = axios.create({
  baseURL: SAMPLE_BACKEND_URL,
  timeout: 10000,
});

const sampleAiServerClient = axios.create({
  baseURL: SAMPLE_AI_SERVER_URL,
  timeout: 10000,
});

/**
 * Handle fetch backend health for the current workflow.
 */
export async function fetchBackendHealth(): Promise<HealthResponse> {
  const response = await backendClient.get<HealthResponse>("/api/v1/spec-runs/health");
  return response.data;
}

/**
 * Handle fetch ai server health for the current workflow.
 */
export async function fetchAiServerHealth(): Promise<HealthResponse> {
  const response = await aiServerClient.get<HealthResponse>("/health");
  return response.data;
}

/**
 * Handle fetch sample backend health for the current workflow.
 */
export async function fetchSampleBackendHealth(): Promise<HealthResponse> {
  const response = await sampleBackendClient.get<{ status: string }>("/actuator/health");
  return {
    status: response.data.status,
    service: "sample-service-backend",
  };
}

/**
 * Handle fetch sample ai server health for the current workflow.
 */
export async function fetchSampleAiServerHealth(): Promise<HealthResponse> {
  const response = await sampleAiServerClient.get<HealthResponse>("/health");
  return response.data;
}

/**
 * Handle fetch sample backend summary for the current workflow.
 */
export async function fetchSampleBackendSummary(): Promise<unknown> {
  const response = await sampleBackendClient.get("/api/v1/generated/sample-service/summary");
  return response.data;
}

/**
 * Run spec bundle for the current workflow.
 */
export async function runSpecBundle(
  projectId: string,
  documents: SpecDocument[],
  ragEnabled: boolean,
  workspacePath: string,
): Promise<SpecRunResponse> {
  const response = await backendClient.post<SpecRunResponse>("/api/v1/spec-runs", {
    projectId,
    documents,
    ragEnabled,
    dryRun: false,
    workspacePath,
  });
  return response.data;
}

/**
 * Stream spec bundle for the current workflow.
 */
export async function streamSpecBundle(
  projectId: string,
  documents: SpecDocument[],
  ragEnabled: boolean,
  workspacePath: string,
  onEvent: (event: SpecRunStreamEvent) => void,
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${BACKEND_URL}/api/v1/spec-runs/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        projectId,
        documents,
        ragEnabled,
        dryRun: false,
        workspacePath,
      }),
    });
  } catch (error) {
    throw new Error(await buildStreamNetworkErrorMessage(error));
  }

  if (!response.ok || !response.body) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const text = await response.text();
      if (text) {
        try {
          const payload = JSON.parse(text) as { message?: string; code?: string };
          if (payload.message) {
            detail = payload.message;
          } else {
            detail = text;
          }
        } catch {
          detail = text;
        }
      }
    } catch {
      // Ignore body parsing errors and keep the HTTP status text.
    }
    throw new Error(`stream request failed: ${detail}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) {
        continue;
      }
      onEvent(JSON.parse(trimmed) as SpecRunStreamEvent);
    }
  }
}

async function buildStreamNetworkErrorMessage(error: unknown): Promise<string> {
  const backendHealthy = await canReachUrl(`${BACKEND_URL}/api/v1/spec-runs/health`);
  const aiHealthy = await canReachUrl(`${AI_SERVER_URL}/health`);

  if (!backendHealthy && !aiHealthy) {
    return `dashboard backend와 AI server에 연결할 수 없습니다. \`python specyn.py up -d\`로 대시보드 스택을 다시 기동하세요. backend=${BACKEND_URL}, ai=${AI_SERVER_URL}`;
  }

  if (!backendHealthy) {
    return `dashboard backend에 연결할 수 없습니다. \`python specyn.py up -d\`로 backend를 다시 기동하세요. backend=${BACKEND_URL}`;
  }

  if (!aiHealthy) {
    return `dashboard AI server에 연결할 수 없습니다. \`python specyn.py up -d\`로 AI server를 다시 기동하세요. ai=${AI_SERVER_URL}`;
  }

  const message = error instanceof Error ? error.message : String(error);
  return `network error while starting stream request: ${message}`;
}

async function canReachUrl(url: string): Promise<boolean> {
  try {
    const response = await fetch(url, {
      method: "GET",
    });
    return response.ok;
  } catch {
    return false;
  }
}
