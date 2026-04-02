package com.sample.service.global.error;

import java.time.Instant;

public record ErrorResponse(
        String code,
        String message,
        String path,
        Instant timestamp
) {
}
