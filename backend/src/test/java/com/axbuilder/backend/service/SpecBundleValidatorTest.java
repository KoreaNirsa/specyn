package com.axbuilder.backend.service;

import com.axbuilder.backend.dto.SpecDocument;
import com.axbuilder.backend.dto.SpecRunRequest;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class SpecBundleValidatorTest {

    private final SpecBundleValidator validator = new SpecBundleValidator();

    @Test
    void passesWhenAllRequiredSpecsExist() {
        SpecRunRequest request = new SpecRunRequest(
                "todo-service",
                List.of(
                        document("product", validContent()),
                        document("api", validContent()),
                        document("test", validContent()),
                        document("review", validContent()),
                        agentDocument()
                ),
                false,
                true,
                ".workspace/todo-service"
        );

        assertThatCode(() -> validator.validate(request)).doesNotThrowAnyException();
    }

    @Test
    void failsWhenARequiredSpecIsMissing() {
        SpecRunRequest request = new SpecRunRequest(
                "todo-service",
                List.of(
                        document("product", validContent()),
                        document("api", validContent())
                ),
                false,
                true,
                ".workspace/todo-service"
        );

        assertThatThrownBy(() -> validator.validate(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("필수 spec 누락");
    }

    @Test
    void failsWhenRequiredAgentIsMissingFromExecutionFlow() {
        SpecRunRequest request = new SpecRunRequest(
                "todo-service",
                List.of(
                        document("product", validContent()),
                        document("api", validContent()),
                        document("test", validContent()),
                        document("review", validContent()),
                        invalidAgentDocument()
                ),
                false,
                true,
                ".workspace/todo-service"
        );

        assertThatThrownBy(() -> validator.validate(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("필수 agent 누락");
    }

    @Test
    void failsWhenFeedbackLoopCanOnlyRunAfterItsAgentHasNotExecutedYet() {
        SpecRunRequest request = new SpecRunRequest(
                "todo-service",
                List.of(
                        document("product", validContent()),
                        document("api", validContent()),
                        document("test", validContent()),
                        document("review", validContent()),
                        invalidFeedbackAgentDocument()
                ),
                false,
                true,
                ".workspace/todo-service"
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
        return """
                # 목적
                text
                # 입력
                text
                # 출력
                text
                # 실행 규칙
                text
                # Validation 기준
                text
                # Prompt
                ## Role
                text
                ## Instructions
                text
                ## Format
                text
                """;
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
                id: todo-service-agent
                type: agent
                version: 1.1.0
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
                max_feedback_rounds: 1
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

                # 목적
                text
                # 입력
                text
                # 출력
                text
                # 실행 규칙
                text
                # Validation 기준
                text
                # Prompt
                ## Role
                text
                ## Instructions
                text
                ## Format
                text
                """;
    }
}
