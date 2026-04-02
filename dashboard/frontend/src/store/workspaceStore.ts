import { create } from "zustand";
import { persist } from "zustand/middleware";

import { DEFAULT_DOCS } from "../lib/defaultSpecs";
import { AgentStepResult, RunHistoryEntry, SpecRunStreamEvent, SpecType } from "../types";

interface WorkspaceState {
  documents: Record<SpecType, string>;
  results: AgentStepResult[];
  eventTrace: SpecRunStreamEvent[];
  runStatus: string;
  currentRunId: string | null;
  currentProjectId: string | null;
  currentWorkspacePath: string | null;
  runHistory: RunHistoryEntry[];
  setDocument: (type: SpecType, content: string) => void;
  resetDocuments: () => void;
  setResults: (results: AgentStepResult[]) => void;
  upsertResult: (result: AgentStepResult) => void;
  clearRun: () => void;
  appendEvent: (event: SpecRunStreamEvent) => void;
  setRunState: (payload: {
    runStatus?: string;
    currentRunId?: string | null;
    currentProjectId?: string | null;
    currentWorkspacePath?: string | null;
  }) => void;
  pushHistory: (entry: RunHistoryEntry) => void;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  persist(
    (set) => ({
      documents: DEFAULT_DOCS,
      results: [],
      eventTrace: [],
      runStatus: "READY",
      currentRunId: null,
      currentProjectId: null,
      currentWorkspacePath: null,
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
      upsertResult: (result) =>
        set((state) => {
          const nextResults = [...state.results];
          const existingIndex = nextResults.findIndex((item) => item.agent === result.agent);
          if (existingIndex >= 0) {
            nextResults[existingIndex] = result;
          } else {
            nextResults.push(result);
          }
          return { results: nextResults };
        }),
      clearRun: () =>
        set({
          results: [],
          eventTrace: [],
          runStatus: "READY",
          currentRunId: null,
          currentProjectId: null,
          currentWorkspacePath: null,
        }),
      appendEvent: (event) =>
        set((state) => ({
          eventTrace: [...state.eventTrace, event].slice(-200),
        })),
      setRunState: (payload) =>
        set((state) => ({
          runStatus: payload.runStatus ?? state.runStatus,
          currentRunId: payload.currentRunId === undefined ? state.currentRunId : payload.currentRunId,
          currentProjectId: payload.currentProjectId === undefined ? state.currentProjectId : payload.currentProjectId,
          currentWorkspacePath:
            payload.currentWorkspacePath === undefined ? state.currentWorkspacePath : payload.currentWorkspacePath,
        })),
      pushHistory: (entry) =>
        set((state) => ({
          runHistory: [entry, ...state.runHistory].slice(0, 12),
        })),
    }),
    {
      name: "specyn-dashboard-workspace",
      version: 2,
      partialize: (state) => ({
        documents: state.documents,
        runHistory: state.runHistory,
      }),
    },
  ),
);
