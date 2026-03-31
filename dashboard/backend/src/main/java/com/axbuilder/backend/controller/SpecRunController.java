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

import java.util.Map;

@RestController
@RequestMapping("/api/v1/spec-runs")
public class SpecRunController {

    private final SpecRunService specRunService;

    public SpecRunController(SpecRunService specRunService) {
        this.specRunService = specRunService;
    }

    @PostMapping
    public ResponseEntity<SpecRunResponse> create(@Valid @RequestBody SpecRunRequest request) {
        return ResponseEntity.ok(specRunService.run(request));
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}
