package com.axbuilder.backend.config;

import io.github.cdimascio.dotenv.Dotenv;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Provide dotenv config behavior for the current module.
 */
@Slf4j
@Configuration
public class DotenvConfig {

    /**
     * Handle dotenv for the current workflow.
     */
    @Bean
    public Dotenv dotenv() {
        Dotenv dotenv = Dotenv.configure()
                .ignoreIfMissing()
                .load();
        log.info("dotenv initialized");
        return dotenv;
    }
}
