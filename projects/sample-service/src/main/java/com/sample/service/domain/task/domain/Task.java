package com.sample.service.domain.task.domain;

import com.sample.service.common.enums.TaskStatus;

import java.util.UUID;

public record Task(
        UUID id,
        String title,
        TaskStatus status
) {
}
