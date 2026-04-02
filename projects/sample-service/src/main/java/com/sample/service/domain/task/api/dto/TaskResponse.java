package com.sample.service.domain.task.api.dto;

import com.sample.service.common.enums.TaskStatus;
import com.sample.service.domain.task.domain.Task;

import java.util.UUID;

public record TaskResponse(
        UUID id,
        String title,
        TaskStatus status
) {
    public static TaskResponse from(Task task) {
        return new TaskResponse(task.id(), task.title(), task.status());
    }
}
