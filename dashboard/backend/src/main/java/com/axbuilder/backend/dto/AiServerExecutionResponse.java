package com.axbuilder.backend.dto;

import java.util.List;

public record AiServerExecutionResponse(
        String status,
        String summary,
        List<String> generatedFiles,
        List<String> validations
) {
}
