package com.axbuilder.backend.controller;

import com.axbuilder.backend.dto.SpecRunRequest;
import com.axbuilder.backend.dto.SpecRunResponse;
import com.axbuilder.backend.service.SpecRunService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.StreamingResponseBody;

import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;

/**
 * Provide spec run controller behavior for the current module.
 */
@RestController
@RequestMapping("/api/v1/spec-runs")
public class SpecRunController {

    private final SpecRunService specRunService;

    /**
     * Handle spec run controller for the current workflow.
     */
    public SpecRunController(SpecRunService specRunService) {
        this.specRunService = specRunService;
    }

    /**
     * Create routine for the current module.
     */
    @PostMapping
    public ResponseEntity<SpecRunResponse> create(@Valid @RequestBody SpecRunRequest request) {
        return ResponseEntity.ok(specRunService.run(request));
    }

    /**
     * Stream routine for the current module.
     */
    @PostMapping(value = "/stream", produces = "application/x-ndjson")
    public StreamingResponseBody stream(@Valid @RequestBody SpecRunRequest request) {
        specRunService.validateRequest(request);
        String runId = UUID.randomUUID().toString();
        return outputStream -> {
            try {
                specRunService.stream(
                        request,
                        event -> {
                            try {
                                outputStream.write((event + "\n").getBytes(StandardCharsets.UTF_8));
                                outputStream.flush();
                            } catch (Exception exception) {
                                throw new RuntimeException(exception);
                            }
                        }
                    );
            } catch (Exception exception) {
                outputStream.write(
                        (
                                specRunService.buildErrorEvent(
                                        runId,
                                        request.projectId(),
                                        exception.getMessage() == null ? "stream failed" : exception.getMessage()
                                ) + "\n"
                        ).getBytes(StandardCharsets.UTF_8)
                );
                outputStream.flush();
            }
        };
    }

    /**
     * Handle health for the current workflow.
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
