import axios from "axios";

import { HealthResponse, SpecDocument, SpecRunResponse } from "../types";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8180";
const AI_SERVER_URL = import.meta.env.VITE_AI_SERVER_URL ?? "http://localhost:8100";

const backendClient = axios.create({
  baseURL: BACKEND_URL,
  timeout: 30000,
});

const aiServerClient = axios.create({
  baseURL: AI_SERVER_URL,
  timeout: 30000,
});

export async function fetchBackendHealth(): Promise<HealthResponse> {
  const response = await backendClient.get<HealthResponse>("/api/v1/spec-runs/health");
  return response.data;
}

export async function fetchAiServerHealth(): Promise<HealthResponse> {
  const response = await aiServerClient.get<HealthResponse>("/health");
  return response.data;
}

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
