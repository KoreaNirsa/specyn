export type SpecType = "spec" | "api" | "tasks" | "review" | "plan";
export type SpecDocumentType = "product" | "api" | "test" | "review" | "agent";

export interface SpecDocument {
  name: string;
  type: SpecDocumentType;
  content: string;
}

export interface AgentStepResult {
  agent: string;
  status: string;
  summary: string;
  executor?: string;
  generatedFiles: string[];
  validations: string[];
}

export interface SpecRunResponse {
  runId: string;
  projectId: string;
  workspacePath: string;
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
  workspacePath: string;
  status: string;
  createdAt: string;
  resultCount: number;
}

export interface SpecRunStreamEvent {
  type: "run-start" | "step-start" | "step-log" | "step-complete" | "run-complete" | "run-error";
  runId: string;
  projectId: string;
  workspacePath?: string;
  totalSteps?: number;
  stepIndex?: number;
  agent?: string;
  message?: string;
  status?: string;
  summary?: string;
  executor?: string;
  generatedFiles?: string[];
  validations?: string[];
  resultCount?: number;
}
