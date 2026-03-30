package com.axbuilder.backend.generated.sample_service;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

@RestController
public class GeneratedSampleServiceController {

    private final AtomicLong sequence = new AtomicLong(0);
    private final Map<Long, Map<String, Object>> store = Collections.synchronizedMap(new LinkedHashMap<>());

    public GeneratedSampleServiceController() {
        seedItem("Spec bundle 검증", "sample-service spec를 validate 하고 generated page를 확인합니다.", "DONE");
        seedItem("런타임 확인", "새 항목을 추가하고 상태를 변경한 뒤 삭제까지 확인합니다.", "PENDING");
    }

    @GetMapping("/api/v1/generated/sample-service/summary")
    public Map<String, Object> generatedSummary() {
        Map<String, Object> payload = buildPayload("GET", "/api/v1/generated/sample-service/summary", "generated project summary");
        payload.put("scenarios", List.of("사용자가 generated 페이지에서 제목과 설명을 입력해 새 작업을 생성한다.", "사용자가 작업 목록을 확인하고 특정 작업의 상세 JSON 응답을 본다.", "사용자가 작업 상태를 `PENDING` ↔ `DONE` 으로 전환한다.", "사용자가 잘못 만든 작업을 삭제하고 목록이 즉시 갱신되는 것을 확인한다.", "개발자는 동일한 spec bundle로 API 계약, generated frontend, generated backend, generated docs가 함께 갱신되는지 확인한다."));
        payload.put("endpointCount", 5);
        payload.put("sampleMode", "task-crud-demo");
        payload.put("taskCount", listItems().size());
        payload.put("sampleRoute", "/generated/sample-service");
        return payload;
    }

    @GetMapping("/api/v1/tasks")
    public Map<String, Object> listTasks() {
        Map<String, Object> payload = buildPayload("GET", "/api/v1/tasks", "작업 목록 조회");
        List<Map<String, Object>> tasks = listItems();
        payload.put("items", tasks);
        payload.put("count", tasks.size());
        return payload;
    }

    @GetMapping("/api/v1/tasks/{id}")
    public ResponseEntity<Map<String, Object>> getTask(@PathVariable Long id) {
        Map<String, Object> task = findStoredItem(id);
        if (task == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(errorPayload("NOT_FOUND", "작업을 찾을 수 없습니다.", "/api/v1/tasks/{id}"));
        }
        Map<String, Object> payload = buildPayload("GET", "/api/v1/tasks/{id}", "작업 단건 조회");
        payload.put("item", copyItem(task));
        return ResponseEntity.ok(payload);
    }

    @PostMapping("/api/v1/tasks")
    public ResponseEntity<Map<String, Object>> createTask(@RequestBody(required = false) Map<String, Object> body) {
        String title = readText(body, "title");
        if (title.isBlank()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(errorPayload("VALIDATION_ERROR", "title 필드는 필수입니다.", "/api/v1/tasks"));
        }
        String description = readText(body, "description");
        Map<String, Object> created = seedItem(title, description, "PENDING");
        Map<String, Object> payload = buildPayload("POST", "/api/v1/tasks", "작업 생성");
        payload.put("item", created);
        payload.put("count", listItems().size());
        return ResponseEntity.status(HttpStatus.CREATED).body(payload);
    }

    @PatchMapping("/api/v1/tasks/{id}/status")
    public ResponseEntity<Map<String, Object>> updateTaskStatus(@PathVariable Long id, @RequestBody(required = false) Map<String, Object> body) {
        Map<String, Object> task = findStoredItem(id);
        if (task == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(errorPayload("NOT_FOUND", "작업을 찾을 수 없습니다.", "/api/v1/tasks/{id}/status"));
        }

        String status = readText(body, "status").toUpperCase();
        if (!("PENDING".equals(status) || "DONE".equals(status))) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(errorPayload("INVALID_STATUS", "status는 PENDING 또는 DONE 이어야 합니다.", "/api/v1/tasks/{id}/status"));
        }

        synchronized (store) {
            task.put("status", status);
            task.put("updatedAt", Instant.now().toString());
        }

        Map<String, Object> payload = buildPayload("PATCH", "/api/v1/tasks/{id}/status", "작업 상태 변경");
        payload.put("item", copyItem(task));
        return ResponseEntity.ok(payload);
    }

    @DeleteMapping("/api/v1/tasks/{id}")
    public ResponseEntity<?> deleteTask(@PathVariable Long id) {
        Map<String, Object> removed;
        synchronized (store) {
            removed = store.remove(id);
        }
        if (removed == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(errorPayload("NOT_FOUND", "작업을 찾을 수 없습니다.", "/api/v1/tasks/{id}"));
        }
        return ResponseEntity.noContent().build();
    }

    private Map<String, Object> seedItem(String title, String description, String status) {
        long id = sequence.incrementAndGet();
        Map<String, Object> item = new LinkedHashMap<>();
        item.put("id", id);
        item.put("title", title);
        item.put("description", description);
        item.put("status", status);
        item.put("createdAt", Instant.now().toString());
        item.put("updatedAt", Instant.now().toString());
        synchronized (store) {
            store.put(id, item);
        }
        return copyItem(item);
    }

    private List<Map<String, Object>> listItems() {
        List<Map<String, Object>> items;
        synchronized (store) {
            items = new ArrayList<>(store.values());
        }
        Collections.reverse(items);
        List<Map<String, Object>> copied = new ArrayList<>();
        for (Map<String, Object> item : items) {
            copied.add(copyItem(item));
        }
        return copied;
    }

    private Map<String, Object> findStoredItem(Long id) {
        synchronized (store) {
            return store.get(id);
        }
    }

    private String readText(Map<String, Object> body, String key) {
        if (body == null) {
            return "";
        }
        Object value = body.get(key);
        return value == null ? "" : String.valueOf(value).trim();
    }

    private Map<String, Object> errorPayload(String code, String message, String path) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("code", code);
        payload.put("message", message);
        payload.put("path", path);
        payload.put("timestamp", Instant.now().toString());
        return payload;
    }

    private Map<String, Object> copyItem(Map<String, Object> item) {
        return new LinkedHashMap<>(item);
    }

    private Map<String, Object> buildPayload(String method, String path, String description) {
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("projectId", "sample-service");
        payload.put("title", "Sample Service");
        payload.put("method", method);
        payload.put("path", path);
        payload.put("description", description);
        payload.put("summary", "Specyn 사용자가 `specyn.py run`까지 실행했을 때 실제로 생성 결과를 눈으로 확인할 수 있는 간단한 작업 관리 웹사이트의 요구사항을 정의한다.");
        payload.put("generatedBy", "specyn-local-runtime");
        payload.put("executionFlow", List.of("planner", "design", "api", "backend", "frontend", "dba", "devops", "test", "code-analysis", "security", "performance", "review", "docs", "final-review"));
        return payload;
    }
}
