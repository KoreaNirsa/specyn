package com.axbuilder.backend.support;

import lombok.Builder;
import lombok.Getter;

import java.time.OffsetDateTime;

@Getter
@Builder
public class ApiErrorResponse {
    private final String code;
    private final String message;
    private final String path;
    private final OffsetDateTime timestamp;
}
