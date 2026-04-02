package com.sample.service.domain.task.domain;

import com.sample.service.common.enums.TaskStatus;
import java.time.Instant;
import java.util.UUID;

public class Task {
    private final UUID id;
    private final String title;
    private final String description;
    private final TaskStatus status;
    private final Instant createdAt;
    private final Instant updatedAt;

    public Task(
            UUID id,
            String title,
            String description,
            TaskStatus status,
            Instant createdAt,
            Instant updatedAt
    ) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.status = status;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public UUID getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getDescription() {
        return description;
    }

    public TaskStatus getStatus() {
        return status;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
