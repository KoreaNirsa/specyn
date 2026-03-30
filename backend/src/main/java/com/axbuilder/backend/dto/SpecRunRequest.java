package com.axbuilder.backend.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;

import java.util.List;

public record SpecRunRequest(
        @NotBlank String projectId,
        @NotEmpty List<@Valid SpecDocument> documents,
        boolean ragEnabled,
        boolean dryRun,
        String workspacePath
) {
}
