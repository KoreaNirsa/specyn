from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tools.spec_contracts import DEFAULT_AGENT_FLOW
from tools.spec_loader import SpecDocument


@dataclass(slots=True)
class FeedbackLoop:
    name: str
    trigger_after: str
    agents: list[str]
    max_rounds: int


@dataclass(slots=True)
class AgentFlow:
    execution_flow: list[str]
    optional_agents: list[str]
    supported_agents: list[str]
    max_feedback_rounds: int = 0
    feedback_loops: list[FeedbackLoop] = field(default_factory=list)


@dataclass(slots=True)
class ExecutionStep:
    agent: str
    label: str
    phase: str
    round_number: int


def normalize_agent_name(agent_name: str) -> str:
    return agent_name.strip().lower().replace("_", "-").replace(" ", "-")


def normalize_identifier(value: str) -> str:
    return normalize_agent_name(value).strip("-") or "step"


def _parse_agent_list(raw_value: Any) -> list[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, str):
        values = [item.strip() for item in raw_value.split(",")]
    elif isinstance(raw_value, list):
        values = [str(item).strip() for item in raw_value]
    else:
        return []

    return [normalize_agent_name(value) for value in values if value]


def _coerce_non_negative_int(raw_value: Any, default: int) -> int:
    if isinstance(raw_value, bool):
        return default
    if isinstance(raw_value, int):
        return max(raw_value, 0)
    if isinstance(raw_value, str):
        try:
            return max(int(raw_value.strip()), 0)
        except ValueError:
            return default
    return default


def _parse_feedback_loops(raw_value: Any, *, default_rounds: int) -> list[FeedbackLoop]:
    if not isinstance(raw_value, list):
        return []

    feedback_loops: list[FeedbackLoop] = []
    for index, item in enumerate(raw_value, start=1):
        if not isinstance(item, dict):
            continue

        trigger_after_raw = item.get("trigger_after")
        trigger_after = (
            normalize_agent_name(str(trigger_after_raw)) if trigger_after_raw is not None else ""
        )
        agents = _parse_agent_list(item.get("agents"))
        loop_name = normalize_identifier(
            str(item.get("name") or f"feedback-loop-{index}-{trigger_after or 'unknown'}")
        )
        max_rounds = _coerce_non_negative_int(item.get("max_rounds"), default_rounds)
        feedback_loops.append(
            FeedbackLoop(
                name=loop_name,
                trigger_after=trigger_after,
                agents=agents,
                max_rounds=max_rounds,
            )
        )

    return feedback_loops


def resolve_agent_flow(
    bundle: dict[str, SpecDocument],
    *,
    rag_enabled: bool,
) -> AgentFlow:
    agent_document = bundle.get("agent")

    execution_flow = DEFAULT_AGENT_FLOW.copy()
    optional_agents: list[str] = []
    supported_agents = execution_flow.copy()
    max_feedback_rounds = 0
    feedback_loops: list[FeedbackLoop] = []

    if agent_document is not None:
        metadata = agent_document.metadata
        execution_flow = _parse_agent_list(metadata.get("execution_flow")) or execution_flow
        optional_agents = _parse_agent_list(metadata.get("optional_agents"))
        supported_agents = _parse_agent_list(metadata.get("supported_agents")) or list(
            dict.fromkeys([*execution_flow, *optional_agents])
        )
        max_feedback_rounds = _coerce_non_negative_int(metadata.get("max_feedback_rounds"), 0)
        feedback_loops = _parse_feedback_loops(
            metadata.get("feedback_loops"),
            default_rounds=max_feedback_rounds,
        )

    if rag_enabled and "rag" in supported_agents and "rag" not in execution_flow:
        if "planner" in execution_flow:
            planner_index = execution_flow.index("planner")
            execution_flow = execution_flow.copy()
            execution_flow.insert(planner_index + 1, "rag")
        else:
            execution_flow = ["rag", *execution_flow]

    return AgentFlow(
        execution_flow=execution_flow,
        optional_agents=optional_agents,
        supported_agents=supported_agents,
        max_feedback_rounds=max_feedback_rounds,
        feedback_loops=feedback_loops,
    )


def build_execution_plan(
    bundle: dict[str, SpecDocument],
    *,
    rag_enabled: bool,
) -> list[ExecutionStep]:
    flow = resolve_agent_flow(bundle, rag_enabled=rag_enabled)
    steps: list[ExecutionStep] = []
    sequence = 1

    loops_by_trigger: dict[str, list[FeedbackLoop]] = {}
    for loop in flow.feedback_loops:
        loops_by_trigger.setdefault(loop.trigger_after, []).append(loop)

    for agent_name in flow.execution_flow:
        steps.append(
            ExecutionStep(
                agent=agent_name,
                label=f"{sequence:02d}-{agent_name}",
                phase="main",
                round_number=0,
            )
        )
        sequence += 1

        for loop in loops_by_trigger.get(agent_name, []):
            if loop.max_rounds <= 0 or not loop.agents:
                continue

            for round_number in range(1, loop.max_rounds + 1):
                for feedback_agent in loop.agents:
                    steps.append(
                        ExecutionStep(
                            agent=feedback_agent,
                            label=(f"{sequence:02d}-{feedback_agent}-{loop.name}-r{round_number}"),
                            phase=loop.name,
                            round_number=round_number,
                        )
                    )
                    sequence += 1

    return steps
