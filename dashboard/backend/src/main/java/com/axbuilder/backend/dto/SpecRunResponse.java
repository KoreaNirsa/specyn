package com.axbuilder.backend.dto;

import java.util.List;

/**
 * Provide spec run response behavior for the current module.
 */
public record SpecRunResponse(
        String runId,
        String projectId,
        String workspacePath,
        String status,
        List<AgentStepResult> results
) {
}
