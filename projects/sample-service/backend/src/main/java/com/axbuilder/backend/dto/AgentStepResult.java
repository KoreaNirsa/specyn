package com.axbuilder.backend.dto;

import com.axbuilder.backend.agent.AgentType;

import java.util.List;

public record AgentStepResult(
        AgentType agent,
        String status,
        String summary,
        List<String> generatedFiles,
        List<String> validations
) {
}
