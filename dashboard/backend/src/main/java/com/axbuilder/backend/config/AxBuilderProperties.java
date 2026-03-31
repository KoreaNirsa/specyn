package com.axbuilder.backend.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "axbuilder.ai")
public record AxBuilderProperties(String baseUrl, int timeoutSeconds) {
}
