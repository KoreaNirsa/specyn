package com.axbuilder.backend.dto;

import com.axbuilder.backend.agent.AgentType;

import java.util.List;

/**
 * Provide agent step result behavior for the current module.
 */
public record AgentStepResult(
        AgentType agent,
        String status,
        String summary,
        String executor,
        List<String> generatedFiles,
        List<String> validations
) {
}
