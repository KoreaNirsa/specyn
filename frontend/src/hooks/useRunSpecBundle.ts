import { useMutation } from "@tanstack/react-query";

import { runSpecBundle } from "../api/client";
import { useWorkspaceStore } from "../store/workspaceStore";
import { RunFormValues, SpecDocument, SpecType } from "../types";

function toSpecDocuments(documents: Record<SpecType, string>): SpecDocument[] {
  return (Object.entries(documents) as Array<[SpecType, string]>).map(([type, content]) => ({
    name: `${type}.md`,
    type,
    content,
  }));
}

export function useRunSpecBundle() {
  const documents = useWorkspaceStore((state) => state.documents);
  const setResults = useWorkspaceStore((state) => state.setResults);

  return useMutation({
    mutationFn: async (values: RunFormValues) => {
      return runSpecBundle(
        values.projectId,
        toSpecDocuments(documents),
        values.ragEnabled,
        values.workspacePath,
      );
    },
    onSuccess: (response) => {
      setResults(response.results);
    },
  });
}
