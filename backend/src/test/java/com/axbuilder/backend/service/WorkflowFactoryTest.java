package com.axbuilder.backend.service;

import com.axbuilder.backend.agent.AgentType;
import com.axbuilder.backend.dto.SpecDocument;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

class WorkflowFactoryTest {

    private final WorkflowFactory workflowFactory = new WorkflowFactory();

    @Test
    void buildsConfiguredFlowFromAgentSpec() {
        List<AgentType> flow = workflowFactory.build(List.of(agentDocument()), false);
        assertThat(flow).containsExactly(
                AgentType.PLANNER,
                AgentType.DESIGN,
                AgentType.API,
                AgentType.BACKEND,
                AgentType.API,
                AgentType.BACKEND,
                AgentType.FRONTEND,
                AgentType.DESIGN,
                AgentType.FRONTEND,
                AgentType.DBA,
                AgentType.BACKEND,
                AgentType.DBA,
                AgentType.DEVOPS,
                AgentType.TEST,
                AgentType.CODE_ANALYSIS,
                AgentType.SECURITY,
                AgentType.PERFORMANCE,
                AgentType.REVIEW,
                AgentType.DOCS,
                AgentType.REVIEW,
                AgentType.DOCS,
                AgentType.FINAL_REVIEW
        );
    }

    @Test
    void includesRagWhenEnabledAndSupported() {
        List<AgentType> flow = workflowFactory.build(List.of(agentDocument()), true);
        assertThat(flow).containsSequence(AgentType.PLANNER, AgentType.RAG, AgentType.DESIGN);
    }

    private SpecDocument agentDocument() {
        return new SpecDocument("agent.md", "agent", """
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
                  - docs
                  - final-review
                max_feedback_rounds: 1
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
