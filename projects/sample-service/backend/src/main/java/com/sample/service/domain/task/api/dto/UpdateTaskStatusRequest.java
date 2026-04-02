package com.sample.service.domain.task.api.dto;

import com.sample.service.common.enums.TaskStatus;
import jakarta.validation.constraints.NotNull;

public record UpdateTaskStatusRequest(
        @NotNull(message = "status is required")
        TaskStatus status
) {
}
