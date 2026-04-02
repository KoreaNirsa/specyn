package com.axbuilder.backend.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Provide app config behavior for the current module.
 */
@Configuration
@EnableConfigurationProperties(AxBuilderProperties.class)
public class AppConfig {
}
