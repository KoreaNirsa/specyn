package com.axbuilder.backend.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Configuration
@EnableConfigurationProperties(AxBuilderProperties.class)
public class AppConfig {
}
