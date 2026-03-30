package com.axbuilder.backend.generated.sample_service;

            import org.springframework.http.HttpStatus;
            import org.springframework.http.ResponseEntity;
            import org.springframework.web.bind.annotation.DeleteMapping;
            import org.springframework.web.bind.annotation.GetMapping;
            import org.springframework.web.bind.annotation.PatchMapping;
            import org.springframework.web.bind.annotation.PathVariable;
            import org.springframework.web.bind.annotation.PostMapping;
            import org.springframework.web.bind.annotation.PutMapping;
            import org.springframework.web.bind.annotation.RequestBody;
            import org.springframework.web.bind.annotation.RestController;

            import java.util.LinkedHashMap;
            import java.util.List;
            import java.util.Map;

            @RestController
            public class GeneratedSampleServiceController {


@GetMapping("/api/v1/generated/sample-service/summary")
public Map<String, Object> generatedSummary() {
    Map<String, Object> payload = buildPayload("GET", "/api/v1/generated/sample-service/summary", "generated project summary");
    payload.put("scenarios", List.of("시나리오 1", "시나리오 2", "시나리오 3"));
    payload.put("endpointCount", 2);
    return payload;
}


@GetMapping("/api/v1/example")
public ResponseEntity<Map<String, Object>> getApiV1Example() {
    Map<String, Object> payload = buildPayload("GET", "/api/v1/example", "목록 조회");
    return ResponseEntity.status(HttpStatus.valueOf(200)).body(payload);
}


        @PostMapping("/api/v1/example")
        public ResponseEntity<Map<String, Object>> postApiV1Example(@RequestBody(required = false) Map<String, Object> body) {
            Map<String, Object> payload = buildPayload("POST", "/api/v1/example", "생성");
            if (body != null) {
    payload.put("requestBody", body);
}
return ResponseEntity.status(HttpStatus.valueOf(201)).body(payload);
        }


                private Map<String, Object> buildPayload(String method, String path, String description) {
                    Map<String, Object> payload = new LinkedHashMap<>();
                    payload.put("projectId", "sample-service");
                    payload.put("title", "Sample Service");
                    payload.put("method", method);
                    payload.put("path", path);
                    payload.put("description", description);
                    payload.put("summary", "이 문서는 서비스의 제품 목표, 사용자 가치, 성공 기준을 정의하고 downstream spec의 기준점을 제공한다.");
                    payload.put("generatedBy", "specyn-local-runtime");
                    payload.put("executionFlow", List.of("planner", "design", "api", "backend", "frontend", "dba", "devops", "test", "code-analysis", "security", "performance", "review", "docs", "final-review"));
                    return payload;
                }
            }
