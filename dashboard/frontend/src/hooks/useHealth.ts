import { useQuery } from "@tanstack/react-query";

import { fetchAiServerHealth, fetchBackendHealth } from "../api/client";

/**
 * Handle use backend health for the current workflow.
 */
export function useBackendHealth() {
  return useQuery({
    queryKey: ["backend-health"],
    queryFn: fetchBackendHealth,
    refetchInterval: 10000,
  });
}

/**
 * Handle use ai server health for the current workflow.
 */
export function useAiServerHealth() {
  return useQuery({
    queryKey: ["ai-server-health"],
    queryFn: fetchAiServerHealth,
    refetchInterval: 10000,
  });
}
