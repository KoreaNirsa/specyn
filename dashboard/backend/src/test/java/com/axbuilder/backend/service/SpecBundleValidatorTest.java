package com.axbuilder.backend.service;

import com.axbuilder.backend.dto.SpecDocument;
import com.axbuilder.backend.dto.SpecRunRequest;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Provide spec bundle validator test behavior for the current module.
 */
class SpecBundleValidatorTest {

    private static final String PROJECT_ID = "sample-service";
    private static final String WORKSPACE_PATH = "projects/sample-service";
    private static final String GOAL = "# \uBAA9\uC801";
    private static final String INPUT = "# \uC785\uB825";
    private static final String OUTPUT = "# \uCD9C\uB825";
    private static final String RULES = "# \uC2E4\uD589 \uADDC\uCE59";
    private static final String VALIDATION = "# Validation \uAE30\uC900";

    private final SpecBundleValidator validator = new SpecBundleValidator();

    @Test
    void passesWhenAllRequiredSpecsExist() {
        SpecRunRequest request = new SpecRunRequest(
                PROJECT_ID,
                List.of(
                        document("product", validContent()),
                        document("api", validContent()),
                        document("test", validContent()),
                        document("review", validContent()),
                        agentDocument()
                ),
                false,
                true,
                WORKSPACE_PATH
        );

        assertThatCode(() -> validator.validate(request)).doesNotThrowAnyException();
    }

    @Test
    void failsWhenARequiredSpecIsMissing() {
        SpecRunRequest request = new SpecRunRequest(
                PROJECT_ID,
                List.of(
                        document("product", validContent()),
                        document("api", validContent())
                ),
                false,
                true,
                WORKSPACE_PATH
        );

        assertThatThrownBy(() -> validator.validate(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("required spec missing");
    }

    @Test
    void failsWhenWorkspacePathIsNotSampleService() {
        SpecRunRequest request = new SpecRunRequest(
                PROJECT_ID,
                List.of(
                        document("product", validContent()),
                        document("api", validContent()),
                        document("test", validContent()),
                        document("review", validContent()),
                        agentDocument()
                ),
                false,
                true,
                ".workspace/sample-service"
        );

        assertThatThrownBy(() -> validator.validate(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("workspacePath must be " + WORKSPACE_PATH);
    }

    @Test
    void failsWhenRequiredAgentIsMissingFromExecutionFlow() {
        SpecRunRequest request = new SpecRunRequest(
                PROJECT_ID,
                List.of(
                        document("product", validContent()),
                        document("api", validContent()),
                        document("test", validContent()),
                        document("review", validContent()),
                        invalidAgentDocument()
                ),
                false,
                true,
                WORKSPACE_PATH
        );

        assertThatThrownBy(() -> validator.validate(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("required agent missing");
    }

    @Test
    void failsWhenFeedbackLoopCanOnlyRunAfterItsAgentHasNotExecutedYet() {
        SpecRunRequest request = new SpecRunRequest(
                PROJECT_ID,
                List.of(
                        document("product", validContent()),
                        document("api", validContent()),
                        document("test", validContent()),
                        document("review", validContent()),
                        invalidFeedbackAgentDocument()
                ),
                false,
                true,
                WORKSPACE_PATH
        );

        assertThatThrownBy(() -> validator.validate(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("feedback agent frontend")
                .hasMessageContaining("trigger_after design");
    }

    private SpecDocument document(String type, String content) {
        return new SpecDocument(type + ".md", type, content);
    }

    private SpecDocument agentDocument() {
        return new SpecDocument("agent.md", "agent", agentContent(true, false));
    }

    private SpecDocument invalidAgentDocument() {
        return new SpecDocument("agent.md", "agent", agentContent(false, false));
    }

    private SpecDocument invalidFeedbackAgentDocument() {
        return new SpecDocument("agent.md", "agent", agentContent(true, true));
    }

    private String validContent() {
        return GOAL + "\ntext\n"
                + INPUT + "\ntext\n"
                + OUTPUT + "\ntext\n"
                + RULES + "\ntext\n"
                + VALIDATION + "\ntext\n"
                + "# Prompt\n"
                + "## Role\ntext\n"
                + "## Instructions\ntext\n"
                + "## Format\ntext\n";
    }

    private String agentContent(boolean includeFinalReview, boolean invalidFeedbackLoop) {
        String flow = includeFinalReview ? """
                  - docs
                  - final-review
                """ : """
                  - docs
                """;

        String designFrontendLoop = invalidFeedbackLoop ? """
                  - name: invalid-design-frontend-loop
                    trigger_after: design
                    agents:
                      - frontend
                """ : """
                  - name: design-frontend-ux-sync
                    trigger_after: frontend
                    agents:
                      - design
                      - frontend
                """;

        return """
                ---
                id: sample-service-agent
                type: agent
                version: 1.3.0
                owner_agent: orchestrator
                status: draft
                depends_on: [product, api, test, review]
                execution_flow:
                  - planner
                  - design
                  - api
                  - backend
                  - frontend
                  - dba
                  - devops
                  - test
                  - code-analysis
                  - security
                  - performance
                  - review
                """ + flow + """
                max_feedback_rounds: 2
                feedback_loops:
                  - name: api-backend-contract-sync
                    trigger_after: backend
                    agents:
                      - api
                      - backend
                """ + designFrontendLoop + """
                  - name: backend-dba-persistence-hardening
                    trigger_after: dba
                    agents:
                      - backend
                      - dba
                  - name: review-docs-release-sync
                    trigger_after: docs
                    agents:
                      - review
                      - docs
                supported_agents:
                  - planner
                  - design
                  - api
                  - backend
                  - frontend
                  - dba
                  - devops
                  - test
                  - code-analysis
                  - security
                  - performance
                  - review
                  - docs
                  - final-review
                ---
                """
                + validContent();
    }
}
