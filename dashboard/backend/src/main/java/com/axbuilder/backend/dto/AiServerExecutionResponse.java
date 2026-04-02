package com.axbuilder.backend.dto;

import java.util.List;

/**
 * Provide ai server execution response behavior for the current module.
 */
public record AiServerExecutionResponse(
        String status,
        String summary,
        String executor,
        List<String> generatedFiles,
        List<String> validations
) {
}
