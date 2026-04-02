import { useMutation } from "@tanstack/react-query";

import { streamSpecBundle } from "../api/client";
import { useWorkspaceStore } from "../store/workspaceStore";
import { AgentStepResult, RunFormValues, SpecDocument, SpecRunStreamEvent, SpecType } from "../types";

/**
 * Handle to spec documents for the current workflow.
 */
function toSpecDocuments(documents: Record<SpecType, string>): SpecDocument[] {
  return (Object.entries(documents) as Array<[SpecType, string]>).map(([type, content]) => ({
    name: `${type}.md`,
    type,
    content,
  }));
}

/**
 * Handle use run spec bundle for the current workflow.
 */
export function useRunSpecBundle() {
  const documents = useWorkspaceStore((state) => state.documents);
  const clearRun = useWorkspaceStore((state) => state.clearRun);
  const upsertResult = useWorkspaceStore((state) => state.upsertResult);
  const appendEvent = useWorkspaceStore((state) => state.appendEvent);
  const setRunState = useWorkspaceStore((state) => state.setRunState);
  const pushHistory = useWorkspaceStore((state) => state.pushHistory);

  return useMutation({
    mutationFn: async (values: RunFormValues) => {
      clearRun();
      setRunState({
        runStatus: "RUNNING",
        currentProjectId: values.projectId,
        currentWorkspacePath: values.workspacePath,
      });

      let runId = "";
      let resultCount = 0;
      let runErrorMessage = "";

      await streamSpecBundle(
        values.projectId,
        toSpecDocuments(documents),
        values.ragEnabled,
        values.workspacePath,
        (event) => {
          appendEvent(event);
          handleEvent(event, upsertResult, setRunState);
          if (event.runId) {
            runId = event.runId;
          }
          if (event.type === "step-complete") {
            resultCount += 1;
          }
          if (event.type === "run-error") {
            runErrorMessage = event.message ?? "run failed";
          }
        },
      );

      if (runErrorMessage) {
        throw new Error(runErrorMessage);
      }

      return {
        runId,
        resultCount,
      };
    },
    onSuccess: (response, variables) => {
      pushHistory({
        runId: response.runId,
        projectId: variables.projectId,
        workspacePath: variables.workspacePath,
        status: "COMPLETED",
        createdAt: new Date().toISOString(),
        resultCount: response.resultCount,
      });
      setRunState({
        runStatus: "COMPLETED",
        currentRunId: response.runId,
      });
    },
    onError: () => {
      setRunState({ runStatus: "FAILED" });
    },
  });
}

function handleEvent(
  event: SpecRunStreamEvent,
  upsertResult: (result: AgentStepResult) => void,
  setRunState: (payload: {
    runStatus?: string;
    currentRunId?: string | null;
    currentProjectId?: string | null;
    currentWorkspacePath?: string | null;
  }) => void,
) {
  if (event.type === "run-start") {
    setRunState({
      runStatus: "RUNNING",
      currentRunId: event.runId,
      currentProjectId: event.projectId,
      currentWorkspacePath: event.workspacePath ?? null,
    });
    return;
  }

  if (event.type === "step-complete" && event.agent) {
    upsertResult({
      agent: event.agent,
      status: event.status ?? "COMPLETED",
      summary: event.summary ?? "",
      executor: event.executor,
      generatedFiles: event.generatedFiles ?? [],
      validations: event.validations ?? [],
    });
    return;
  }

  if (event.type === "run-complete") {
    setRunState({ runStatus: event.status ?? "COMPLETED" });
    return;
  }

  if (event.type === "run-error") {
    setRunState({ runStatus: "FAILED" });
  }
}
