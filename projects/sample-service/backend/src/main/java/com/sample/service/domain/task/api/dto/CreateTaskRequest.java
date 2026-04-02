package com.sample.service.domain.task.api.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateTaskRequest(
        @NotBlank(message = "title is required")
        @Size(max = 200, message = "title must be at most 200 characters")
        String title,
        @Size(max = 2000, message = "description must be at most 2000 characters")
        String description
) {
}
