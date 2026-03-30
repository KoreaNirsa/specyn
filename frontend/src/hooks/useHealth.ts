import { useQuery } from "@tanstack/react-query";

import { fetchAiServerHealth, fetchBackendHealth } from "../api/client";

export function useBackendHealth() {
  return useQuery({
    queryKey: ["backend-health"],
    queryFn: fetchBackendHealth,
    refetchInterval: 10000,
  });
}

export function useAiServerHealth() {
  return useQuery({
    queryKey: ["ai-server-health"],
    queryFn: fetchAiServerHealth,
    refetchInterval: 10000,
  });
}
