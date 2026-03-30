import { create } from "zustand";

import { DEFAULT_DOCS } from "../lib/defaultSpecs";
import { AgentStepResult, SpecType } from "../types";

interface WorkspaceState {
  documents: Record<SpecType, string>;
  results: AgentStepResult[];
  setDocument: (type: SpecType, content: string) => void;
  resetDocuments: () => void;
  setResults: (results: AgentStepResult[]) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  documents: DEFAULT_DOCS,
  results: [],
  setDocument: (type, content) =>
    set((state) => ({
      documents: {
        ...state.documents,
        [type]: content,
      },
    })),
  resetDocuments: () => set({ documents: DEFAULT_DOCS }),
  setResults: (results) => set({ results }),
}));
