package com.axbuilder.backend.dto;

import com.axbuilder.backend.agent.AgentType;

import java.util.List;

public record AiServerExecutionRequest(
        AgentType agent,
        String projectId,
        List<SpecDocument> documents,
        List<AgentStepResult> previousResults,
        String workspacePath,
        boolean dryRun
) {
}
