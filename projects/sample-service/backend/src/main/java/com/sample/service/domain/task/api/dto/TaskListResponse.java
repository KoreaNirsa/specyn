package com.sample.service.domain.task.api.dto;

import java.util.List;

public record TaskListResponse(
        List<TaskDto> items,
        int count
) {
}
