package com.sample.service.global.error;

import java.time.OffsetDateTime;

public record ErrorResponse(
        String code,
        String message,
        String path,
        OffsetDateTime timestamp
) {
    public static ErrorResponse of(ErrorCode code, String message, String path) {
        return new ErrorResponse(code.name(), message, path, OffsetDateTime.now());
    }
}
