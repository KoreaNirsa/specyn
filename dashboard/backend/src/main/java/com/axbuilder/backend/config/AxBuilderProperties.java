package com.axbuilder.backend.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Provide ax builder properties behavior for the current module.
 */
@ConfigurationProperties(prefix = "axbuilder.ai")
public record AxBuilderProperties(String baseUrl, int timeoutSeconds) {
}
