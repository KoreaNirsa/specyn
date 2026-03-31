import { create } from "zustand";
import { persist } from "zustand/middleware";

import { DEFAULT_DOCS } from "../lib/defaultSpecs";
import { AgentStepResult, RunHistoryEntry, SpecType } from "../types";

interface WorkspaceState {
  documents: Record<SpecType, string>;
  results: AgentStepResult[];
  runHistory: RunHistoryEntry[];
  setDocument: (type: SpecType, content: string) => void;
  resetDocuments: () => void;
  setResults: (results: AgentStepResult[]) => void;
  pushHistory: (entry: RunHistoryEntry) => void;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  persist(
    (set) => ({
      documents: DEFAULT_DOCS,
      results: [],
      runHistory: [],
      setDocument: (type, content) =>
        set((state) => ({
          documents: {
            ...state.documents,
            [type]: content,
          },
        })),
      resetDocuments: () => set({ documents: DEFAULT_DOCS }),
      setResults: (results) => set({ results }),
      pushHistory: (entry) =>
        set((state) => ({
          runHistory: [entry, ...state.runHistory].slice(0, 12),
        })),
    }),
    {
      name: "specyn-dashboard-workspace",
      partialize: (state) => ({
        documents: state.documents,
        runHistory: state.runHistory,
      }),
    },
  ),
);
