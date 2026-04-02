package com.axbuilder.backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Provide ax builder application behavior for the current module.
 */
@SpringBootApplication
public class AxBuilderApplication {

    /**
     * Run the main entry point for the current module.
     */
    public static void main(String[] args) {
        SpringApplication.run(AxBuilderApplication.class, args);
    }
}
