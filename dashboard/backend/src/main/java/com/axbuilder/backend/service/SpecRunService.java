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
                            response.generatedFiles(),
                            response.validations()
                    )
            );
        }

        return new SpecRunResponse(UUID.randomUUID().toString(), "COMPLETED", results);
    }
}
