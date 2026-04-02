package com.sample.service.domain.task.api.dto;

import com.sample.service.common.enums.TaskStatus;
import com.sample.service.domain.task.domain.Task;
import java.time.Instant;
import java.util.UUID;

public record TaskDto(
        UUID id,
        String title,
        String description,
        TaskStatus status,
        Instant createdAt,
        Instant updatedAt
) {
    public static TaskDto from(Task task) {
        return new TaskDto(
                task.getId(),
                task.getTitle(),
                task.getDescription(),
                task.getStatus(),
                task.getCreatedAt(),
                task.getUpdatedAt()
        );
    }
}
