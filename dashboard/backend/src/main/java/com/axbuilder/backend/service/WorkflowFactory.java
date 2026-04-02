package com.axbuilder.backend.service;

import com.axbuilder.backend.agent.AgentType;
import com.axbuilder.backend.dto.SpecDocument;
import org.springframework.stereotype.Component;
import org.yaml.snakeyaml.Yaml;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Provide workflow factory behavior for the current module.
 */
@Component
public class WorkflowFactory {

    private static final Pattern FRONT_MATTER_PATTERN = Pattern.compile("^---\\n(.*?)\\n---\\n", Pattern.DOTALL);
    private static final List<AgentType> DEFAULT_FLOW = List.of(
            AgentType.PLANNER,
            AgentType.API,
            AgentType.TEST,
            AgentType.REVIEW,
            AgentType.DOCS,
            AgentType.FINAL_REVIEW
    );

    /**
     * Build routine for the current module.
     */
    public List<AgentType> build(List<SpecDocument> documents, boolean ragEnabled) {
        List<AgentType> baseFlow = new ArrayList<>(resolveConfiguredFlow(documents).orElse(DEFAULT_FLOW));
        Set<AgentType> supportedAgents = resolveSupportedAgents(documents);

        if (ragEnabled && supportedAgents.contains(AgentType.RAG) && !baseFlow.contains(AgentType.RAG)) {
            int plannerIndex = baseFlow.indexOf(AgentType.PLANNER);
            if (plannerIndex >= 0) {
                baseFlow.add(plannerIndex + 1, AgentType.RAG);
            } else {
                baseFlow.add(0, AgentType.RAG);
            }
        }

        Optional<Map<String, Object>> metadataOptional = resolveAgentMetadata(documents);
        int defaultRounds = metadataOptional
                .flatMap(metadata -> toNonNegativeInt(metadata.get("max_feedback_rounds")))
                .orElse(0);
        List<FeedbackLoop> feedbackLoops = metadataOptional
                .map(metadata -> parseFeedbackLoops(metadata.get("feedback_loops"), defaultRounds))
                .orElseGet(List::of);

        if (feedbackLoops.isEmpty()) {
            return baseFlow;
        }

        Map<AgentType, List<FeedbackLoop>> loopsByTrigger = new LinkedHashMap<>();
        for (FeedbackLoop feedbackLoop : feedbackLoops) {
            if (feedbackLoop.maxRounds() <= 0 || feedbackLoop.agents().isEmpty()) {
                continue;
            }
            loopsByTrigger.computeIfAbsent(feedbackLoop.triggerAfter(), key -> new ArrayList<>())
                    .add(feedbackLoop);
        }

        if (loopsByTrigger.isEmpty()) {
            return baseFlow;
        }

        List<AgentType> executionPlan = new ArrayList<>();
        for (AgentType agentType : baseFlow) {
            executionPlan.add(agentType);
            List<FeedbackLoop> triggeredLoops = loopsByTrigger.get(agentType);
            if (triggeredLoops == null || triggeredLoops.isEmpty()) {
                continue;
            }
            for (FeedbackLoop feedbackLoop : triggeredLoops) {
                for (int round = 0; round < feedbackLoop.maxRounds(); round++) {
                    executionPlan.addAll(feedbackLoop.agents());
                }
            }
        }

        return executionPlan;
    }

    /**
     * Resolve configured flow for the current workflow.
     */
    private Optional<List<AgentType>> resolveConfiguredFlow(List<SpecDocument> documents) {
        return resolveAgentMetadata(documents)
                .map(metadata -> metadata.get("execution_flow"))
                .flatMap(this::toAgentFlow);
    }

    /**
     * Resolve supported agents for the current workflow.
     */
    private Set<AgentType> resolveSupportedAgents(List<SpecDocument> documents) {
        return resolveAgentMetadata(documents)
                .map(metadata -> {
                    Set<AgentType> supported = new LinkedHashSet<>();
                    toAgentFlow(metadata.get("supported_agents")).ifPresent(supported::addAll);
                    toAgentFlow(metadata.get("optional_agents")).ifPresent(supported::addAll);
                    toAgentFlow(metadata.get("execution_flow")).ifPresent(supported::addAll);
                    return supported.isEmpty() ? new LinkedHashSet<>(DEFAULT_FLOW) : supported;
                })
                .orElseGet(() -> new LinkedHashSet<>(DEFAULT_FLOW));
    }

    /**
     * Resolve agent metadata for the current workflow.
     */
    private Optional<Map<String, Object>> resolveAgentMetadata(List<SpecDocument> documents) {
        return documents.stream()
                .filter(document -> "agent".equals(document.type()))
                .findFirst()
                .flatMap(document -> parseFrontMatter(document.content()));
    }

    /**
     * Parse front matter for the current workflow.
     */
    private Optional<Map<String, Object>> parseFrontMatter(String content) {
        Matcher matcher = FRONT_MATTER_PATTERN.matcher(content);
        if (!matcher.find()) {
            return Optional.empty();
        }

        Object loaded = new Yaml().load(matcher.group(1));
        if (loaded instanceof Map<?, ?> rawMap) {
            @SuppressWarnings("unchecked")
            Map<String, Object> metadata = (Map<String, Object>) rawMap;
            return Optional.of(metadata);
        }
        return Optional.empty();
    }

    /**
     * Handle to agent flow for the current workflow.
     */
    private Optional<List<AgentType>> toAgentFlow(Object rawValue) {
        if (!(rawValue instanceof List<?> rawList) || rawList.isEmpty()) {
            return Optional.empty();
        }

        List<AgentType> flow = rawList.stream()
                .map(String::valueOf)
                .map(AgentType::fromValue)
                .toList();
        return Optional.of(flow);
    }

    /**
     * Handle to non negative int for the current workflow.
     */
    private Optional<Integer> toNonNegativeInt(Object rawValue) {
        if (rawValue instanceof Integer integerValue && integerValue >= 0) {
            return Optional.of(integerValue);
        }
        return Optional.empty();
    }

    /**
     * Parse feedback loops for the current workflow.
     */
    private List<FeedbackLoop> parseFeedbackLoops(Object rawValue, int defaultRounds) {
        if (!(rawValue instanceof List<?> rawList) || rawList.isEmpty()) {
            return List.of();
        }

        List<FeedbackLoop> feedbackLoops = new ArrayList<>();
        for (Object item : rawList) {
            if (!(item instanceof Map<?, ?> rawLoop)) {
                continue;
            }

            try {
                AgentType triggerAfter = AgentType.fromValue(String.valueOf(rawLoop.get("trigger_after")));
                List<AgentType> agents = toAgentFlow(rawLoop.get("agents")).orElse(List.of());
                int maxRounds = toNonNegativeInt(rawLoop.get("max_rounds")).orElse(defaultRounds);
                feedbackLoops.add(new FeedbackLoop(triggerAfter, agents, maxRounds));
            } catch (IllegalArgumentException ignored) {
                // validator가 잘못된 스펙을 차단하므로 런타임에서는 안전하게 무시한다.
            }
        }

        return feedbackLoops;
    }

    /**
     * Provide feedback loop behavior for the current module.
     */
    private record FeedbackLoop(AgentType triggerAfter, List<AgentType> agents, int maxRounds) {
    }
}
