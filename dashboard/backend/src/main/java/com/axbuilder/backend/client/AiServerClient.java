package com.axbuilder.backend.client;

import com.axbuilder.backend.config.AxBuilderProperties;
import com.axbuilder.backend.dto.AgentStepResult;
import com.axbuilder.backend.dto.AiServerExecutionRequest;
import com.axbuilder.backend.dto.AiServerExecutionResponse;
import com.axbuilder.backend.dto.SpecDocument;
import org.springframework.boot.json.JsonParser;
import org.springframework.boot.json.JsonParserFactory;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

/**
 * Client for the dashboard AI server.
 */
@Component
public class AiServerClient {

    private final HttpClient httpClient;
    private final JsonParser jsonParser;
    private final String baseUrl;
    private final Duration timeout;

    public AiServerClient(AxBuilderProperties properties) {
        this.baseUrl = properties.baseUrl();
        this.timeout = Duration.ofSeconds(properties.timeoutSeconds());
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(this.timeout)
                .version(HttpClient.Version.HTTP_1_1)
                .build();
        this.jsonParser = JsonParserFactory.getJsonParser();
    }

    public AiServerExecutionResponse execute(AiServerExecutionRequest request) {
        try {
            HttpRequest httpRequest = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/v1/agents/execute"))
                    .header("Content-Type", "application/json; charset=utf-8")
                    .timeout(timeout)
                    .POST(HttpRequest.BodyPublishers.ofString(toJson(request)))
                    .build();

            HttpResponse<String> response = httpClient.send(
                    httpRequest,
                    HttpResponse.BodyHandlers.ofString()
            );

            if (response.statusCode() >= 400) {
                String body = response.body();
                String message = body == null || body.isBlank()
                        ? "status=" + response.statusCode()
                        : body;
                throw new IllegalStateException("dashboard ai-server request failed: " + message);
            }

            return fromJson(response.body());
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("dashboard ai-server request was interrupted.", exception);
        } catch (IOException exception) {
            throw new IllegalStateException("dashboard ai-server is unavailable: " + exception.getMessage(), exception);
        }
    }

    public AiServerExecutionResponse streamExecute(
            AiServerExecutionRequest request,
            Consumer<String> logSink
    ) {
        try {
            HttpRequest httpRequest = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/v1/agents/execute/stream"))
                    .header("Content-Type", "application/json; charset=utf-8")
                    .timeout(timeout)
                    .POST(HttpRequest.BodyPublishers.ofString(toJson(request)))
                    .build();

            HttpResponse<java.io.InputStream> response = httpClient.send(
                    httpRequest,
                    HttpResponse.BodyHandlers.ofInputStream()
            );

            if (response.statusCode() >= 400) {
                String body = new String(response.body().readAllBytes(), StandardCharsets.UTF_8);
                String message = body == null || body.isBlank()
                        ? "status=" + response.statusCode()
                        : body;
                throw new IllegalStateException("dashboard ai-server request failed: " + message);
            }

            try (
                    BufferedReader reader = new BufferedReader(
                            new InputStreamReader(response.body(), StandardCharsets.UTF_8)
                    )
            ) {
                String line;
                AiServerExecutionResponse completed = null;
                while ((line = reader.readLine()) != null) {
                    if (line.isBlank()) {
                        continue;
                    }
                    completed = consumeStreamLine(line, logSink, completed);
                }
                if (completed == null) {
                    throw new IllegalStateException("dashboard ai-server stream finished without a completion payload.");
                }
                return completed;
            }
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("dashboard ai-server request was interrupted.", exception);
        } catch (IOException exception) {
            throw new IllegalStateException("dashboard ai-server is unavailable: " + exception.getMessage(), exception);
        }
    }

    private String toJson(AiServerExecutionRequest request) {
        return "{"
                + "\"agent\":" + toJsonValue(request.agent().value())
                + ",\"projectId\":" + toJsonValue(request.projectId())
                + ",\"documents\":" + toDocumentsJson(request.documents())
                + ",\"previousResults\":" + toResultsJson(request.previousResults())
                + ",\"workspacePath\":" + toJsonValue(request.workspacePath())
                + ",\"dryRun\":" + request.dryRun()
                + "}";
    }

    private String toDocumentsJson(List<SpecDocument> documents) {
        List<String> items = new ArrayList<>();
        for (SpecDocument document : documents) {
            items.add(
                    "{"
                            + "\"name\":" + toJsonValue(document.name())
                            + ",\"type\":" + toJsonValue(document.type())
                            + ",\"content\":" + toJsonValue(document.content())
                            + "}"
            );
        }
        return "[" + String.join(",", items) + "]";
    }

    private String toResultsJson(List<AgentStepResult> results) {
        List<String> items = new ArrayList<>();
        for (AgentStepResult result : results) {
            items.add(
                    "{"
                            + "\"agent\":" + toJsonValue(result.agent().value())
                            + ",\"status\":" + toJsonValue(result.status())
                            + ",\"summary\":" + toJsonValue(result.summary())
                            + ",\"generatedFiles\":" + toStringListJson(result.generatedFiles())
                            + ",\"validations\":" + toStringListJson(result.validations())
                            + "}"
            );
        }
        return "[" + String.join(",", items) + "]";
    }

    private String toStringListJson(List<String> items) {
        List<String> values = new ArrayList<>();
        for (String item : items) {
            values.add(toJsonValue(item));
        }
        return "[" + String.join(",", values) + "]";
    }

    private String toJsonValue(String value) {
        if (value == null) {
            return "null";
        }
        return "\"" + value
                .replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r")
                .replace("\t", "\\t")
                + "\"";
    }

    @SuppressWarnings("unchecked")
    private AiServerExecutionResponse fromJson(String body) {
        Map<String, Object> payload = jsonParser.parseMap(body);
        return new AiServerExecutionResponse(
                stringValue(payload.get("status")),
                stringValue(payload.get("summary")),
                stringValue(payload.get("executor")),
                stringList(payload.get("generatedFiles")),
                stringList(payload.get("validations"))
        );
    }

    @SuppressWarnings("unchecked")
    private AiServerExecutionResponse consumeStreamLine(
            String line,
            Consumer<String> logSink,
            AiServerExecutionResponse completed
    ) {
        Map<String, Object> payload = jsonParser.parseMap(line);
        String type = stringValue(payload.get("type"));

        if ("status".equals(type) || "log".equals(type)) {
            String message = stringValue(payload.get("message"));
            if (!message.isBlank()) {
                logSink.accept(message);
            }
            return completed;
        }

        if ("complete".equals(type) && payload.get("response") instanceof Map<?, ?> responseMap) {
            return fromJsonMap((Map<String, Object>) responseMap);
        }

        return completed;
    }

    private AiServerExecutionResponse fromJsonMap(Map<String, Object> payload) {
        return new AiServerExecutionResponse(
                stringValue(payload.get("status")),
                stringValue(payload.get("summary")),
                stringValue(payload.get("executor")),
                stringList(payload.get("generatedFiles")),
                stringList(payload.get("validations"))
        );
    }

    private String stringValue(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private List<String> stringList(Object value) {
        if (!(value instanceof List<?> rawList)) {
            return List.of();
        }
        List<String> items = new ArrayList<>();
        for (Object item : rawList) {
            items.add(String.valueOf(item));
        }
        return items;
    }
}
