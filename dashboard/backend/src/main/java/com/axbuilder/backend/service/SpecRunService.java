package com.axbuilder.backend.service;

import com.axbuilder.backend.agent.AgentType;
import com.axbuilder.backend.client.AiServerClient;
import com.axbuilder.backend.dto.AgentStepResult;
import com.axbuilder.backend.dto.AiServerExecutionRequest;
import com.axbuilder.backend.dto.AiServerExecutionResponse;
import com.axbuilder.backend.dto.SpecRunRequest;
import com.axbuilder.backend.dto.SpecRunResponse;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.function.Consumer;

/**
 * Provide spec run service behavior for the current module.
 */
@Service
public class SpecRunService {

    private final SpecBundleValidator validator;
    private final WorkflowFactory workflowFactory;
    private final AiServerClient aiServerClient;

    public SpecRunService(
            SpecBundleValidator validator,
            WorkflowFactory workflowFactory,
            AiServerClient aiServerClient
    ) {
        this.validator = validator;
        this.workflowFactory = workflowFactory;
        this.aiServerClient = aiServerClient;
    }

    /**
     * Run routine for the current workflow.
     */
    public SpecRunResponse run(SpecRunRequest request) {
        validator.validate(request);

        List<AgentStepResult> results = new ArrayList<>();
        for (AgentType agent : workflowFactory.build(request.documents(), request.ragEnabled())) {
            AiServerExecutionResponse response = aiServerClient.execute(
                    new AiServerExecutionRequest(
                            agent,
                            request.projectId(),
                            request.documents(),
                            results,
                            request.workspacePath(),
                            request.dryRun()
                    )
            );

            results.add(
                    new AgentStepResult(
                            agent,
                            response.status(),
                            response.summary(),
                            response.executor(),
                            response.generatedFiles(),
                            response.validations()
                    )
            );
        }

        return new SpecRunResponse(
                UUID.randomUUID().toString(),
                request.projectId(),
                request.workspacePath(),
                "COMPLETED",
                results
        );
    }

    /**
     * Validate request for the current workflow.
     */
    public void validateRequest(SpecRunRequest request) {
        validator.validate(request);
    }

    /**
     * Stream routine for the current module.
     */
    public void stream(SpecRunRequest request, Consumer<String> eventSink) {
        validator.validate(request);

        String runId = UUID.randomUUID().toString();
        List<AgentType> executionFlow = workflowFactory.build(request.documents(), request.ragEnabled());
        List<AgentStepResult> results = new ArrayList<>();

        eventSink.accept(
                jsonObject(
                        "type", "run-start",
                        "runId", runId,
                        "projectId", request.projectId(),
                        "workspacePath", request.workspacePath(),
                        "totalSteps", executionFlow.size()
                )
        );

        int stepIndex = 0;
        for (AgentType agent : executionFlow) {
            stepIndex += 1;
            int currentStepIndex = stepIndex;
            eventSink.accept(
                    jsonObject(
                            "type", "step-start",
                            "runId", runId,
                            "projectId", request.projectId(),
                            "stepIndex", currentStepIndex,
                            "totalSteps", executionFlow.size(),
                            "agent", agent.name().toLowerCase().replace("_", "-"),
                            "message", agent.name() + " agent execution started"
                    )
            );

            AiServerExecutionResponse response = aiServerClient.streamExecute(
                    new AiServerExecutionRequest(
                            agent,
                            request.projectId(),
                            request.documents(),
                            results,
                            request.workspacePath(),
                            request.dryRun()
                    ),
                    message -> eventSink.accept(
                            jsonObject(
                                    "type", "step-log",
                                    "runId", runId,
                                    "projectId", request.projectId(),
                                    "stepIndex", currentStepIndex,
                                    "totalSteps", executionFlow.size(),
                                    "agent", agent.name().toLowerCase().replace("_", "-"),
                                    "message", message
                            )
                    )
            );

            AgentStepResult result = new AgentStepResult(
                    agent,
                    response.status(),
                    response.summary(),
                    response.executor(),
                    response.generatedFiles(),
                    response.validations()
            );
            results.add(result);

            eventSink.accept(
                    jsonObject(
                            "type", "step-complete",
                            "runId", runId,
                            "projectId", request.projectId(),
                            "stepIndex", currentStepIndex,
                            "totalSteps", executionFlow.size(),
                            "agent", agent.name().toLowerCase().replace("_", "-"),
                            "status", response.status(),
                            "summary", response.summary(),
                            "executor", response.executor(),
                            "generatedFiles", response.generatedFiles(),
                            "validations", response.validations()
                    )
            );
        }

        eventSink.accept(
                jsonObject(
                        "type", "run-complete",
                        "runId", runId,
                        "projectId", request.projectId(),
                        "workspacePath", request.workspacePath(),
                        "status", "COMPLETED",
                        "resultCount", results.size()
                )
        );
    }

    /**
     * Build error event payload for the current workflow.
     */
    public String buildErrorEvent(String runId, String projectId, String message) {
        return jsonObject(
                "type", "run-error",
                "runId", runId,
                "projectId", projectId,
                "status", "FAILED",
                "message", message
        );
    }

    private String jsonObject(Object... pairs) {
        StringBuilder builder = new StringBuilder("{");
        for (int index = 0; index < pairs.length; index += 2) {
            if (index > 0) {
                builder.append(',');
            }
            builder.append('"').append(escapeJson(String.valueOf(pairs[index]))).append('"').append(':');
            builder.append(toJsonValue(pairs[index + 1]));
        }
        builder.append('}');
        return builder.toString();
    }

    private String toJsonValue(Object value) {
        if (value == null) {
            return "null";
        }
        if (value instanceof Number || value instanceof Boolean) {
            return String.valueOf(value);
        }
        if (value instanceof List<?> list) {
            StringBuilder builder = new StringBuilder("[");
            for (int index = 0; index < list.size(); index++) {
                if (index > 0) {
                    builder.append(',');
                }
                builder.append(toJsonValue(list.get(index)));
            }
            builder.append(']');
            return builder.toString();
        }
        return "\"" + escapeJson(String.valueOf(value)) + "\"";
    }

    private String escapeJson(String value) {
        return value
                .replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r");
    }
}
