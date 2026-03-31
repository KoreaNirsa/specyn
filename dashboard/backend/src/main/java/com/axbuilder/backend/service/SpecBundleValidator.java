package com.axbuilder.backend.service;

import com.axbuilder.backend.agent.AgentType;
import com.axbuilder.backend.dto.SpecDocument;
import com.axbuilder.backend.dto.SpecRunRequest;
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
import java.util.stream.Collectors;

@Component
public class SpecBundleValidator {

    private static final Set<String> REQUIRED_TYPES = Set.of("product", "api", "test", "review", "agent");
    private static final List<String> REQUIRED_HEADINGS = List.of(
            "# 목적",
            "# 입력",
            "# 출력",
            "# 실행 규칙",
            "# Validation 기준",
            "# Prompt"
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

    public void validate(SpecRunRequest request) {
        Set<String> provided = request.documents()
                .stream()
                .map(SpecDocument::type)
                .collect(Collectors.toSet());

        Set<String> missing = REQUIRED_TYPES.stream()
                .filter(required -> !provided.contains(required))
                .collect(Collectors.toSet());

        List<String> violations = new ArrayList<>();
        if (!missing.isEmpty()) {
            violations.add("필수 spec 누락: " + missing);
        }

        for (SpecDocument document : request.documents()) {
            for (String heading : REQUIRED_HEADINGS) {
                if (!document.content().contains(heading)) {
                    violations.add(document.name() + " -> 필수 섹션 누락: " + heading);
                }
            }

            if (document.content().contains("# Prompt")) {
                for (String heading : REQUIRED_PROMPT_SUBHEADINGS) {
                    if (!document.content().contains(heading)) {
                        violations.add(document.name() + " -> Prompt 하위 섹션 누락: " + heading);
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

    private void validateDependencies(List<SpecDocument> documents, List<String> violations) {
        Set<String> provided = documents.stream().map(SpecDocument::type).collect(Collectors.toSet());

        for (SpecDocument document : documents) {
            parseFrontMatter(document.content())
                    .map(metadata -> metadata.get("depends_on"))
                    .ifPresent(rawDependsOn -> {
                        if (!(rawDependsOn instanceof List<?> dependsOn)) {
                            violations.add(document.name() + " -> depends_on은 배열이어야 합니다.");
                            return;
                        }
                        for (Object dependency : dependsOn) {
                            String dependencyName = String.valueOf(dependency);
                            if (!provided.contains(dependencyName)) {
                                violations.add(document.name() + " -> depends_on spec 누락: " + dependencyName);
                            }
                        }
                    });
        }
    }

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
            violations.add("agent.md -> execution_flow가 비어 있습니다.");
            return;
        }

        List<AgentType> flow = flowOptional.get();
        Set<AgentType> uniqueFlow = new LinkedHashSet<>(flow);
        if (uniqueFlow.size() != flow.size()) {
            violations.add("agent.md -> execution_flow에 중복 agent가 있습니다.");
        }

        for (AgentType requiredAgent : REQUIRED_FLOW_AGENTS) {
            if (!flow.contains(requiredAgent)) {
                violations.add("agent.md -> 필수 agent 누락: " + requiredAgent.value());
            }
        }

        Set<AgentType> supportedAgents = new LinkedHashSet<>(flow);
        toAgentFlow(metadata.get("supported_agents")).ifPresent(supportedAgents::addAll);
        toAgentFlow(metadata.get("optional_agents")).ifPresent(supportedAgents::addAll);

        toAgentFlow(metadata.get("supported_agents")).ifPresent(supported -> {
            for (AgentType agentType : flow) {
                if (!supported.contains(agentType)) {
                    violations.add(
                            "agent.md -> execution_flow의 " + agentType.value() + " 는 supported_agents에 포함되어야 합니다."
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
            violations.add("agent.md -> max_feedback_rounds는 0 이상의 정수여야 합니다.");
        }

        Object rawFeedbackLoops = metadata.get("feedback_loops");
        if (rawFeedbackLoops == null) {
            return;
        }
        if (!(rawFeedbackLoops instanceof List<?> feedbackLoops)) {
            violations.add("agent.md -> feedback_loops는 배열이어야 합니다.");
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
                violations.add(prefix + " 는 객체여야 합니다.");
                continue;
            }

            Optional<AgentType> triggerAfterOptional = toAgent(loop.get("trigger_after"));
            if (triggerAfterOptional.isEmpty()) {
                violations.add(prefix + " -> trigger_after는 유효한 agent여야 합니다.");
            }

            Object rawAgents = loop.get("agents");
            List<?> agents = rawAgents instanceof List<?> rawAgentList ? rawAgentList : List.of();
            if (agents.isEmpty()) {
                violations.add(prefix + " -> agents는 비어 있지 않은 배열이어야 합니다.");
            }

            if (loop.containsKey("max_rounds") && toNonNegativeInt(loop.get("max_rounds")).isEmpty()) {
                violations.add(prefix + " -> max_rounds는 0 이상의 정수여야 합니다.");
            }

            if (triggerAfterOptional.isEmpty() || agents.isEmpty()) {
                continue;
            }

            AgentType triggerAfter = triggerAfterOptional.get();
            if (!flowIndex.containsKey(triggerAfter)) {
                violations.add(prefix + " -> trigger_after는 execution_flow에 포함되어야 합니다.");
                continue;
            }

            Set<AgentType> uniqueAgents = new LinkedHashSet<>();
            for (Object rawAgent : agents) {
                Optional<AgentType> agentOptional = toAgent(rawAgent);
                if (agentOptional.isEmpty()) {
                    violations.add(prefix + " -> 지원하지 않는 feedback agent가 있습니다: " + rawAgent);
                    continue;
                }

                AgentType agentType = agentOptional.get();
                if (!uniqueAgents.add(agentType)) {
                    violations.add(prefix + " -> agents에 중복 agent가 있습니다: " + agentType.value());
                }
                if (!supportedAgents.contains(agentType)) {
                    violations.add(prefix + " -> feedback agent는 supported_agents에 포함되어야 합니다: " + agentType.value());
                }
                if (!flowIndex.containsKey(agentType)) {
                    violations.add(prefix + " -> feedback agent는 execution_flow에 포함되어야 합니다: " + agentType.value());
                    continue;
                }
                if (flowIndex.get(agentType) > flowIndex.get(triggerAfter)) {
                    violations.add(
                            prefix + " -> feedback agent " + agentType.value() + " 는 trigger_after "
                                    + triggerAfter.value() + " 이전 또는 동일 시점에 있어야 합니다."
                    );
                }
            }
        }
    }

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

    private Optional<Integer> toNonNegativeInt(Object rawValue) {
        if (rawValue instanceof Integer integerValue && integerValue >= 0) {
            return Optional.of(integerValue);
        }
        return Optional.empty();
    }
}
