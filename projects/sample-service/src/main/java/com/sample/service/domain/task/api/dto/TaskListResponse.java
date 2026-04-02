package com.sample.service.domain.task.api.dto;

import java.util.List;

public record TaskListResponse(
        List<TaskResponse> items
) {
}
