import { SpecDocumentType, SpecType } from "../types";

export const SPEC_ORDER: SpecType[] = ["spec", "api", "tasks", "review", "plan"];

export const SPEC_FILE_NAMES: Record<SpecType, string> = {
  spec: "spec.md",
  api: "api.md",
  tasks: "tasks.md",
  review: "review.md",
  plan: "plan.md",
};

export const SPEC_DOCUMENT_TYPES: Record<SpecType, SpecDocumentType> = {
  spec: "product",
  api: "api",
  tasks: "test",
  review: "review",
  plan: "agent",
};

export const SPEC_DOCUMENT_LABELS: Record<SpecType, string> = {
  spec: "Spec",
  api: "API",
  tasks: "Tasks",
  review: "Review",
  plan: "Plan",
};
