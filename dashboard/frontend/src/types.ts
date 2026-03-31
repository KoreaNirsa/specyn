export type SpecType = "product" | "api" | "test" | "review" | "agent";

export interface SpecDocument {
  name: string;
  type: SpecType;
  content: string;
}

export interface AgentStepResult {
  agent: string;
  status: string;
  summary: string;
  generatedFiles: string[];
  validations: string[];
}

export interface SpecRunResponse {
  runId: string;
  status: string;
  results: AgentStepResult[];
}

export interface HealthResponse {
  status: string;
  service?: string;
  model?: string;
  codexMode?: string;
}

export interface RunFormValues {
  projectId: string;
  workspacePath: string;
  ragEnabled: boolean;
}

export interface RunHistoryEntry {
  runId: string;
  projectId: string;
  status: string;
  createdAt: string;
  resultCount: number;
}
