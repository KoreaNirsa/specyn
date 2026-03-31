package com.axbuilder.backend.agent;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonValue;

import java.util.Arrays;

public enum AgentType {
    PLANNER("planner"),
    RAG("rag"),
    DESIGN("design"),
    API("api"),
    BACKEND("backend"),
    FRONTEND("frontend"),
    DBA("dba"),
    DEVOPS("devops"),
    TEST("test"),
    CODE_ANALYSIS("code-analysis"),
    SECURITY("security"),
    PERFORMANCE("performance"),
    REVIEW("review"),
    DOCS("docs"),
    FINAL_REVIEW("final-review"),
    ORCHESTRATOR("orchestrator");

    private final String value;

    AgentType(String value) {
        this.value = value;
    }

    @JsonValue
    public String value() {
        return value;
    }

    @JsonCreator
    public static AgentType fromValue(String rawValue) {
        return Arrays.stream(values())
                .filter(agentType -> agentType.value.equalsIgnoreCase(rawValue))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("지원하지 않는 agent입니다: " + rawValue));
    }
}
