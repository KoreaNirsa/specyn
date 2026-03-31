package com.axbuilder.backend.dto;

import java.util.List;

public record SpecRunResponse(
        String runId,
        String status,
        List<AgentStepResult> results
) {
}
