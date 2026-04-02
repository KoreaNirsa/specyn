package com.axbuilder.backend.service;

import com.axbuilder.backend.agent.AgentType;
import com.axbuilder.backend.dto.SpecDocument;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Provide workflow factory test behavior for the current module.
 */
class WorkflowFactoryTest {

    private final WorkflowFactory workflowFactory = new WorkflowFactory();

    @Test
    void buildsConfiguredFlowFromAgentSpec() {
        List<AgentType> flow = workflowFactory.build(List.of(agentDocument()), false);
        assertThat(flow).startsWith(
                AgentType.PLANNER,
                AgentType.DESIGN,
                AgentType.API,
                AgentType.BACKEND
        );
        assertThat(flow).endsWith(AgentType.FINAL_REVIEW);
        assertThat(flow).containsSequence(AgentType.BACKEND, AgentType.API, AgentType.BACKEND);
        assertThat(flow).containsSequence(AgentType.FRONTEND, AgentType.DESIGN, AgentType.FRONTEND);
        assertThat(flow).containsSequence(AgentType.DBA, AgentType.BACKEND, AgentType.DBA);
        assertThat(flow).containsSequence(AgentType.DOCS, AgentType.REVIEW, AgentType.DOCS);
        assertThat(flow).hasSizeGreaterThan(100);
    }

    @Test
    void includesRagWhenEnabledAndSupported() {
        List<AgentType> flow = workflowFactory.build(List.of(agentDocument()), true);
        assertThat(flow).containsSequence(AgentType.PLANNER, AgentType.RAG, AgentType.DESIGN);
    }

    /**
     * Handle agent document for the current workflow.
     */
    private SpecDocument agentDocument() {
        return new SpecDocument("agent.md", "agent", """
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
                  - docs
                  - final-review
                max_feedback_rounds: 999
                feedback_loops:
                  - name: api-backend-contract-sync
                    trigger_after: backend
                    agents:
                      - api
                      - backend
                  - name: design-frontend-ux-sync
                    trigger_after: frontend
                    agents:
                      - design
                      - frontend
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
                optional_agents:
                  - rag
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
                  - rag
                  - orchestrator
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
                """);
    }
}
