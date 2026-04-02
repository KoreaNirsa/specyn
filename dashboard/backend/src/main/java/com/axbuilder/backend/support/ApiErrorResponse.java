package com.axbuilder.backend.support;

import lombok.Builder;
import lombok.Getter;

import java.time.OffsetDateTime;

/**
 * Provide api error response behavior for the current module.
 */
@Getter
@Builder
public class ApiErrorResponse {
    private final String code;
    private final String message;
    private final String path;
    private final OffsetDateTime timestamp;
}
