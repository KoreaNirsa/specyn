from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.agent_flow import normalize_agent_name, resolve_agent_flow
from tools.spec_contracts import (
    KNOWN_AGENT_NAMES,
    REQUIRED_FLOW_AGENTS,
    REQUIRED_PROMPT_SUBSECTIONS,
    REQUIRED_SECTIONS,
    REQUIRED_SPEC_TYPES,
)
from tools.spec_loader import SpecDocument

AGENTS_DIR = Path(__file__).resolve().parents[1] / "agents"


@dataclass(slots=True)
class ValidationIssue:
    level: str
    code: str
    message: str


def agent_definition_path(agent_name: str) -> Path:
    normalized = normalize_agent_name(agent_name)
    return AGENTS_DIR / f"{normalized}-agent.md"


def _is_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate_document(document: SpecDocument) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    missing_sections = REQUIRED_SECTIONS - set(document.sections.keys())
    for section in sorted(missing_sections):
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="MISSING_SECTION",
                message=f"{document.name}: '{section}' 섹션이 없습니다.",
            )
        )

    required_meta = {"id", "type", "version", "owner_agent", "status", "depends_on"}
    missing_meta = required_meta - set(document.metadata.keys())
    for key in sorted(missing_meta):
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="MISSING_METADATA",
                message=f"{document.name}: '{key}' 메타데이터가 없습니다.",
            )
        )

    owner_agent = document.metadata.get("owner_agent")
    if owner_agent is not None:
        normalized_owner = normalize_agent_name(str(owner_agent))
        if normalized_owner not in KNOWN_AGENT_NAMES:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="UNKNOWN_OWNER_AGENT",
                    message=f"{document.name}: 지원하지 않는 owner_agent='{owner_agent}' 입니다.",
                )
            )

    depends_on = document.metadata.get("depends_on")
    if depends_on is not None and not isinstance(depends_on, list):
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="INVALID_METADATA_TYPE",
                message=f"{document.name}: 'depends_on'은 배열이어야 합니다.",
            )
        )

    prompt_section = document.sections.get("Prompt")
    if prompt_section:
        missing_prompt_subsections = [
            title
            for title in sorted(REQUIRED_PROMPT_SUBSECTIONS)
            if f"## {title}" not in prompt_section and f"### {title}" not in prompt_section
        ]
        for title in missing_prompt_subsections:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="MISSING_PROMPT_SUBSECTION",
                    message=f"{document.name}: Prompt 섹션에 '{title}' 하위 섹션이 없습니다.",
                )
            )

    return issues


def _validate_spec_dependencies(bundle: dict[str, SpecDocument]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for document in bundle.values():
        depends_on = document.metadata.get("depends_on") or []
        if not isinstance(depends_on, list):
            continue
        for dependency in depends_on:
            dependency_name = str(dependency)
            if dependency_name not in bundle:
                issues.append(
                    ValidationIssue(
                        level="ERROR",
                        code="UNKNOWN_SPEC_DEPENDENCY",
                        message=(
                            f"{document.name}: depends_on에 선언된 '{dependency_name}' spec가 bundle에 없습니다."
                        ),
                    )
                )

    temp_marks: set[str] = set()
    perm_marks: set[str] = set()

    def visit(spec_type: str) -> None:
        if spec_type in perm_marks:
            return
        if spec_type in temp_marks:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="SPEC_DEPENDENCY_CYCLE",
                    message=f"spec dependency cycle이 감지되었습니다: '{spec_type}'",
                )
            )
            return

        temp_marks.add(spec_type)
        depends_on = bundle[spec_type].metadata.get("depends_on") or []
        if isinstance(depends_on, list):
            for dependency in depends_on:
                dependency_name = str(dependency)
                if dependency_name in bundle:
                    visit(dependency_name)
        temp_marks.remove(spec_type)
        perm_marks.add(spec_type)

    for spec_type in bundle:
        visit(spec_type)

    return issues


def _validate_agent_definitions(agent_names: set[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for agent_name in sorted(agent_names):
        definition_path = agent_definition_path(agent_name)
        if not definition_path.exists():
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="MISSING_AGENT_DEFINITION",
                    message=(
                        f"agent.md: agent 정의 문서가 없습니다. "
                        f"expected='{definition_path.relative_to(AGENTS_DIR.parent)}'"
                    ),
                )
            )
    return issues


def _validate_feedback_metadata(
    *,
    agent_document: SpecDocument,
    execution_flow: list[str],
    optional_agents: list[str],
    supported_agents: list[str],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    metadata = agent_document.metadata

    max_feedback_rounds = metadata.get("max_feedback_rounds")
    if max_feedback_rounds is not None and not _is_non_negative_int(max_feedback_rounds):
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="INVALID_MAX_FEEDBACK_ROUNDS",
                message="agent.md: max_feedback_rounds는 0 이상의 정수여야 합니다.",
            )
        )

    raw_feedback_loops = metadata.get("feedback_loops")
    if raw_feedback_loops is None:
        return issues

    if not isinstance(raw_feedback_loops, list):
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="INVALID_FEEDBACK_LOOPS_TYPE",
                message="agent.md: feedback_loops는 배열이어야 합니다.",
            )
        )
        return issues

    execution_index = {agent_name: index for index, agent_name in enumerate(execution_flow)}
    supported_set = set(supported_agents) | set(optional_agents) | set(execution_flow)

    for index, loop in enumerate(raw_feedback_loops, start=1):
        prefix = f"agent.md: feedback_loops[{index}]"
        if not isinstance(loop, dict):
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="INVALID_FEEDBACK_LOOP",
                    message=f"{prefix}는 객체여야 합니다.",
                )
            )
            continue

        trigger_after_raw = loop.get("trigger_after")
        trigger_after = (
            normalize_agent_name(str(trigger_after_raw)) if trigger_after_raw is not None else ""
        )
        if not trigger_after:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="MISSING_FEEDBACK_TRIGGER",
                    message=f"{prefix}: trigger_after가 필요합니다.",
                )
            )
        elif trigger_after not in KNOWN_AGENT_NAMES:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="UNKNOWN_AGENT",
                    message=f"{prefix}: 지원하지 않는 trigger_after agent '{trigger_after}' 입니다.",
                )
            )
        elif trigger_after not in execution_index:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="FEEDBACK_TRIGGER_NOT_IN_FLOW",
                    message=(
                        f"{prefix}: trigger_after '{trigger_after}' 는 execution_flow에 포함되어야 합니다."
                    ),
                )
            )

        agents_raw = loop.get("agents")
        if not isinstance(agents_raw, list) or not agents_raw:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="INVALID_FEEDBACK_LOOP_AGENTS",
                    message=f"{prefix}: agents는 비어 있지 않은 배열이어야 합니다.",
                )
            )
            normalized_agents: list[str] = []
        else:
            normalized_agents = [
                normalize_agent_name(str(agent_name))
                for agent_name in agents_raw
                if str(agent_name).strip()
            ]
            if not normalized_agents:
                issues.append(
                    ValidationIssue(
                        level="ERROR",
                        code="INVALID_FEEDBACK_LOOP_AGENTS",
                        message=f"{prefix}: agents에 유효한 agent 이름이 없습니다.",
                    )
                )
            if len(set(normalized_agents)) != len(normalized_agents):
                issues.append(
                    ValidationIssue(
                        level="ERROR",
                        code="DUPLICATED_AGENT_IN_FEEDBACK_LOOP",
                        message=f"{prefix}: agents에 중복 agent가 있습니다.",
                    )
                )

        max_rounds = loop.get("max_rounds")
        if max_rounds is not None and not _is_non_negative_int(max_rounds):
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="INVALID_FEEDBACK_LOOP_MAX_ROUNDS",
                    message=f"{prefix}: max_rounds는 0 이상의 정수여야 합니다.",
                )
            )

        if trigger_after in execution_index:
            trigger_index = execution_index[trigger_after]
            for agent_name in normalized_agents:
                if agent_name not in KNOWN_AGENT_NAMES:
                    issues.append(
                        ValidationIssue(
                            level="ERROR",
                            code="UNKNOWN_AGENT",
                            message=f"{prefix}: 지원하지 않는 agent '{agent_name}' 입니다.",
                        )
                    )
                    continue
                if agent_name not in supported_set:
                    issues.append(
                        ValidationIssue(
                            level="ERROR",
                            code="FEEDBACK_AGENT_NOT_SUPPORTED",
                            message=(
                                f"{prefix}: feedback agent '{agent_name}' 는 supported_agents 또는 execution_flow에 포함되어야 합니다."
                            ),
                        )
                    )
                    continue
                if agent_name not in execution_index:
                    issues.append(
                        ValidationIssue(
                            level="ERROR",
                            code="FEEDBACK_AGENT_NOT_IN_FLOW",
                            message=(
                                f"{prefix}: feedback agent '{agent_name}' 는 execution_flow에 포함되어야 합니다."
                            ),
                        )
                    )
                    continue
                if execution_index[agent_name] > trigger_index:
                    issues.append(
                        ValidationIssue(
                            level="ERROR",
                            code="FEEDBACK_AGENT_ORDER_INVALID",
                            message=(
                                f"{prefix}: feedback agent '{agent_name}' 는 trigger_after '{trigger_after}' 이전 또는 동일 시점에 있어야 합니다."
                            ),
                        )
                    )

    return issues


def _validate_agent_flow(bundle: dict[str, SpecDocument]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    agent_document = bundle.get("agent")
    if agent_document is None:
        return issues

    flow = resolve_agent_flow(bundle, rag_enabled=False)
    execution_flow = flow.execution_flow
    optional_agents = flow.optional_agents
    supported_agents = flow.supported_agents

    if not execution_flow:
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="EMPTY_AGENT_FLOW",
                message="agent.md: execution_flow가 비어 있습니다.",
            )
        )
        return issues

    seen: set[str] = set()
    for agent_name in execution_flow:
        if agent_name not in KNOWN_AGENT_NAMES:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="UNKNOWN_AGENT",
                    message=f"agent.md: 지원하지 않는 agent '{agent_name}' 이(가) execution_flow에 있습니다.",
                )
            )
        if agent_name in seen:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="DUPLICATED_AGENT_IN_FLOW",
                    message=f"agent.md: execution_flow에 '{agent_name}' 가 중복 선언되었습니다.",
                )
            )
        seen.add(agent_name)

    missing_required_agents = REQUIRED_FLOW_AGENTS - set(execution_flow)
    for agent_name in sorted(missing_required_agents):
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="MISSING_REQUIRED_AGENT",
                message=f"agent.md: execution_flow에 필수 agent '{agent_name}' 이(가) 없습니다.",
            )
        )

    for collection_name, values in {
        "optional_agents": optional_agents,
        "supported_agents": supported_agents,
    }.items():
        for agent_name in values:
            if agent_name not in KNOWN_AGENT_NAMES:
                issues.append(
                    ValidationIssue(
                        level="ERROR",
                        code="UNKNOWN_AGENT",
                        message=(
                            f"agent.md: {collection_name}에 지원하지 않는 agent '{agent_name}' 이(가) 있습니다."
                        ),
                    )
                )

    if supported_agents:
        unsupported_in_flow = [
            agent_name for agent_name in execution_flow if agent_name not in supported_agents
        ]
        for agent_name in unsupported_in_flow:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="FLOW_NOT_IN_SUPPORTED_AGENTS",
                    message=(
                        f"agent.md: execution_flow의 '{agent_name}' 는 supported_agents에 포함되어야 합니다."
                    ),
                )
            )

        optional_not_supported = [
            agent_name for agent_name in optional_agents if agent_name not in supported_agents
        ]
        for agent_name in optional_not_supported:
            issues.append(
                ValidationIssue(
                    level="ERROR",
                    code="OPTIONAL_AGENT_NOT_IN_SUPPORTED_AGENTS",
                    message=(
                        f"agent.md: optional_agents의 '{agent_name}' 는 supported_agents에 포함되어야 합니다."
                    ),
                )
            )

    issues.extend(
        _validate_feedback_metadata(
            agent_document=agent_document,
            execution_flow=execution_flow,
            optional_agents=optional_agents,
            supported_agents=supported_agents,
        )
    )

    referenced_agents = set(execution_flow) | set(optional_agents) | set(supported_agents)
    for loop in flow.feedback_loops:
        referenced_agents.update(loop.agents)
        if loop.trigger_after:
            referenced_agents.add(loop.trigger_after)
    issues.extend(_validate_agent_definitions(referenced_agents))
    return issues


def validate_bundle(bundle: dict[str, SpecDocument]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    missing_types = REQUIRED_SPEC_TYPES - set(bundle.keys())
    for spec_type in sorted(missing_types):
        issues.append(
            ValidationIssue(
                level="ERROR",
                code="MISSING_SPEC",
                message=f"필수 spec '{spec_type}' 이(가) 없습니다.",
            )
        )

    for document in bundle.values():
        issues.extend(validate_document(document))

    issues.extend(_validate_spec_dependencies(bundle))
    issues.extend(_validate_agent_flow(bundle))
    return issues
