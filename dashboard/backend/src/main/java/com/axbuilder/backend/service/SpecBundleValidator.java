package com.axbuilder.backend.service;

import com.axbuilder.backend.agent.AgentType;
import com.axbuilder.backend.dto.SpecDocument;
import com.axbuilder.backend.dto.SpecRunRequest;
import org.springframework.stereotype.Component;
import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.error.YAMLException;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/**
 * Provide spec bundle validator behavior for the current module.
 */
@Component
public class SpecBundleValidator {

    private static final String REQUIRED_PROJECT_ID = "sample-service";
    private static final String REQUIRED_WORKSPACE_PATH = "projects/sample-service";
    private static final String HEADING_GOAL = "# \uBAA9\uC801";
    private static final String HEADING_INPUT = "# \uC785\uB825";
    private static final String HEADING_OUTPUT = "# \uCD9C\uB825";
    private static final String HEADING_RULES = "# \uC2E4\uD589 \uADDC\uCE59";
    private static final String HEADING_VALIDATION = "# Validation \uAE30\uC900";
    private static final String HEADING_PROMPT = "# Prompt";
    private static final Set<String> REQUIRED_TYPES = Set.of("product", "api", "test", "review", "agent");
    private static final List<String> REQUIRED_HEADINGS = List.of(
            HEADING_GOAL,
            HEADING_INPUT,
            HEADING_OUTPUT,
            HEADING_RULES,
            HEADING_VALIDATION,
            HEADING_PROMPT
    );
    private static final List<String> REQUIRED_PROMPT_SUBHEADINGS = List.of(
            "## Role",
            "## Instructions",
            "## Format"
    );
    private static final Set<AgentType> REQUIRED_FLOW_AGENTS = Set.of(
            AgentType.PLANNER,
            AgentType.API,
            AgentType.TEST,
            AgentType.REVIEW,
            AgentType.DOCS,
            AgentType.FINAL_REVIEW
    );
    private static final Pattern FRONT_MATTER_PATTERN = Pattern.compile("^---\\n(.*?)\\n---\\n", Pattern.DOTALL);

    /**
     * Validate routine for the current workflow.
     */
    public void validate(SpecRunRequest request) {
        List<String> violations = new ArrayList<>();
        if (!REQUIRED_PROJECT_ID.equals(request.projectId())) {
            violations.add("projectId must be " + REQUIRED_PROJECT_ID);
        }
        if (!REQUIRED_WORKSPACE_PATH.equals(request.workspacePath())) {
            violations.add("workspacePath must be " + REQUIRED_WORKSPACE_PATH);
        }

        Set<String> provided = request.documents()
                .stream()
                .map(SpecDocument::type)
                .collect(Collectors.toSet());

        Set<String> missing = REQUIRED_TYPES.stream()
                .filter(required -> !provided.contains(required))
                .collect(Collectors.toSet());

        if (!missing.isEmpty()) {
            violations.add("required spec missing: " + missing);
        }

        for (SpecDocument document : request.documents()) {
            for (String heading : REQUIRED_HEADINGS) {
                if (!document.content().contains(heading)) {
                    violations.add(document.name() + " -> required section missing: " + heading);
                }
            }

            if (document.content().contains(HEADING_PROMPT)) {
                for (String heading : REQUIRED_PROMPT_SUBHEADINGS) {
                    if (!document.content().contains(heading)) {
                        violations.add(document.name() + " -> required prompt subsection missing: " + heading);
                    }
                }
            }
        }

        validateDependencies(request.documents(), violations);
        validateAgentFlow(request.documents(), violations);

        if (!violations.isEmpty()) {
            throw new IllegalArgumentException(String.join(" | ", violations));
        }
    }

    /**
     * Validate dependencies for the current workflow.
     */
    private void validateDependencies(List<SpecDocument> documents, List<String> violations) {
        Set<String> provided = documents.stream().map(SpecDocument::type).collect(Collectors.toSet());

        for (SpecDocument document : documents) {
            parseFrontMatter(document.content())
                    .map(metadata -> metadata.get("depends_on"))
                    .ifPresent(rawDependsOn -> {
                        if (!(rawDependsOn instanceof List<?> dependsOn)) {
                            violations.add(document.name() + " -> depends_on must be an array.");
                            return;
                        }
                        for (Object dependency : dependsOn) {
                            String dependencyName = String.valueOf(dependency);
                            if (!provided.contains(dependencyName)) {
                                violations.add(document.name() + " -> depends_on spec missing: " + dependencyName);
                            }
                        }
                    });
        }
    }

    /**
     * Validate agent flow for the current workflow.
     */
    private void validateAgentFlow(List<SpecDocument> documents, List<String> violations) {
        Optional<Map<String, Object>> metadataOptional = documents.stream()
                .filter(document -> "agent".equals(document.type()))
                .findFirst()
                .flatMap(document -> parseFrontMatter(document.content()));

        if (metadataOptional.isEmpty()) {
            return;
        }

        Map<String, Object> metadata = metadataOptional.get();
        Optional<List<AgentType>> flowOptional = toAgentFlow(metadata.get("execution_flow"));
        if (flowOptional.isEmpty()) {
            violations.add("agent.md -> execution_flow must not be empty.");
            return;
        }

        List<AgentType> flow = flowOptional.get();
        Set<AgentType> uniqueFlow = new LinkedHashSet<>(flow);
        if (uniqueFlow.size() != flow.size()) {
            violations.add("agent.md -> execution_flow contains duplicated agents.");
        }

        for (AgentType requiredAgent : REQUIRED_FLOW_AGENTS) {
            if (!flow.contains(requiredAgent)) {
                violations.add("agent.md -> required agent missing: " + requiredAgent.value());
            }
        }

        Set<AgentType> supportedAgents = new LinkedHashSet<>(flow);
        toAgentFlow(metadata.get("supported_agents")).ifPresent(supportedAgents::addAll);
        toAgentFlow(metadata.get("optional_agents")).ifPresent(supportedAgents::addAll);

        toAgentFlow(metadata.get("supported_agents")).ifPresent(supported -> {
            for (AgentType agentType : flow) {
                if (!supported.contains(agentType)) {
                    violations.add(
                            "agent.md -> execution_flow agent must exist in supported_agents: " + agentType.value()
                    );
                }
            }
        });

        validateFeedbackLoops(metadata, flow, supportedAgents, violations);
    }

    private void validateFeedbackLoops(
            Map<String, Object> metadata,
            List<AgentType> flow,
            Set<AgentType> supportedAgents,
            List<String> violations
    ) {
        Object maxFeedbackRounds = metadata.get("max_feedback_rounds");
        if (maxFeedbackRounds != null && toNonNegativeInt(maxFeedbackRounds).isEmpty()) {
            violations.add("agent.md -> max_feedback_rounds must be a non-negative integer.");
        }

        Object rawFeedbackLoops = metadata.get("feedback_loops");
        if (rawFeedbackLoops == null) {
            return;
        }
        if (!(rawFeedbackLoops instanceof List<?> feedbackLoops)) {
            violations.add("agent.md -> feedback_loops must be an array.");
            return;
        }

        Map<AgentType, Integer> flowIndex = new LinkedHashMap<>();
        for (int index = 0; index < flow.size(); index++) {
            flowIndex.put(flow.get(index), index);
        }

        for (int index = 0; index < feedbackLoops.size(); index++) {
            Object rawLoop = feedbackLoops.get(index);
            String prefix = "agent.md -> feedback_loops[" + index + "]";
            if (!(rawLoop instanceof Map<?, ?> loop)) {
                violations.add(prefix + " must be an object.");
                continue;
            }

            Optional<AgentType> triggerAfterOptional = toAgent(loop.get("trigger_after"));
            if (triggerAfterOptional.isEmpty()) {
                violations.add(prefix + " -> trigger_after must be a valid agent.");
            }

            Object rawAgents = loop.get("agents");
            List<?> agents = rawAgents instanceof List<?> rawAgentList ? rawAgentList : List.of();
            if (agents.isEmpty()) {
                violations.add(prefix + " -> agents must be a non-empty array.");
            }

            if (loop.containsKey("max_rounds") && toNonNegativeInt(loop.get("max_rounds")).isEmpty()) {
                violations.add(prefix + " -> max_rounds must be a non-negative integer.");
            }

            if (triggerAfterOptional.isEmpty() || agents.isEmpty()) {
                continue;
            }

            AgentType triggerAfter = triggerAfterOptional.get();
            if (!flowIndex.containsKey(triggerAfter)) {
                violations.add(prefix + " -> trigger_after must exist in execution_flow.");
                continue;
            }

            Set<AgentType> uniqueAgents = new LinkedHashSet<>();
            for (Object rawAgent : agents) {
                Optional<AgentType> agentOptional = toAgent(rawAgent);
                if (agentOptional.isEmpty()) {
                    violations.add(prefix + " -> unsupported feedback agent: " + rawAgent);
                    continue;
                }

                AgentType agentType = agentOptional.get();
                if (!uniqueAgents.add(agentType)) {
                    violations.add(prefix + " -> duplicated feedback agent: " + agentType.value());
                }
                if (!supportedAgents.contains(agentType)) {
                    violations.add(prefix + " -> feedback agent must exist in supported_agents: " + agentType.value());
                }
                if (!flowIndex.containsKey(agentType)) {
                    violations.add(prefix + " -> feedback agent must exist in execution_flow: " + agentType.value());
                    continue;
                }
                if (flowIndex.get(agentType) > flowIndex.get(triggerAfter)) {
                    violations.add(
                            prefix + " -> feedback agent " + agentType.value() + " must appear no later than trigger_after "
                                    + triggerAfter.value()
                    );
                }
            }
        }
    }

    /**
     * Parse front matter for the current workflow.
     */
    private Optional<Map<String, Object>> parseFrontMatter(String content) {
        Matcher matcher = FRONT_MATTER_PATTERN.matcher(content);
        if (!matcher.find()) {
            return Optional.empty();
        }

        try {
            Object loaded = new Yaml().load(matcher.group(1));
            if (loaded instanceof Map<?, ?> rawMap) {
                @SuppressWarnings("unchecked")
                Map<String, Object> metadata = (Map<String, Object>) rawMap;
                return Optional.of(metadata);
            }
            return Optional.empty();
        } catch (YAMLException exception) {
            throw new IllegalArgumentException("front matter parse failed: " + exception.getMessage(), exception);
        }
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
     * Handle to agent for the current workflow.
     */
    private Optional<AgentType> toAgent(Object rawValue) {
        if (rawValue == null) {
            return Optional.empty();
        }
        try {
            return Optional.of(AgentType.fromValue(String.valueOf(rawValue)));
        } catch (IllegalArgumentException ignored) {
            return Optional.empty();
        }
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
}
