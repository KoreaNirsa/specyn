package com.axbuilder.backend.dto;

import jakarta.validation.constraints.NotBlank;

public record SpecDocument(
        @NotBlank String name,
        @NotBlank String type,
        @NotBlank String content
) {
}
