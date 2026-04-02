package com.axbuilder.backend.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * Provide spec document behavior for the current module.
 */
public record SpecDocument(
        @NotBlank String name,
        @NotBlank String type,
        @NotBlank String content
) {
}
