package com.axbuilder.backend.dto;

import com.axbuilder.backend.agent.AgentType;

import java.util.List;

/**
 * Provide ai server execution request behavior for the current module.
 */
public record AiServerExecutionRequest(
        AgentType agent,
        String projectId,
        List<SpecDocument> documents,
        List<AgentStepResult> previousResults,
        String workspacePath,
        boolean dryRun
) {
}
