package com.sample.service.domain.task.api.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateTaskRequest(
        @NotBlank(message = "must not be blank")
        @Size(max = 200, message = "length must be less than or equal to 200")
        String title
) {
}
