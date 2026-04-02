"""
agent spec 메타데이터를 실제 실행 순서와 피드백 루프로 해석하는 흐름 계산 모듈이다.
기본 실행 순서, optional agent, bounded feedback round 규칙을 한곳에서 계산해 프롬프트 컴파일과 로컬 실행기가 동일한 계획을 공유하도록 만든다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tools.spec_contracts import DEFAULT_AGENT_FLOW
from tools.spec_loader import SpecDocument


@dataclass(slots=True)
class FeedbackLoop:
    """
    도구 계층에서 사용되는 `FeedbackLoop` 클래스다.

    Attributes:
        name: 인스턴스가 내부적으로 유지하는 name 관련 상태다.
        trigger_after: 인스턴스가 내부적으로 유지하는 trigger after 관련 상태다.
        agents: 순서대로 처리할 agent 이름 목록이다.
        max_rounds: 인스턴스가 내부적으로 유지하는 max rounds 관련 상태다.
    """
    name: str
    trigger_after: str
    agents: list[str]
    max_rounds: int


@dataclass(slots=True)
class AgentFlow:
    """
    도구 계층에서 사용되는 `AgentFlow` 클래스다.

    Attributes:
        execution_flow: 인스턴스가 내부적으로 유지하는 실행 실행 흐름 관련 상태다.
        optional_agents: 인스턴스가 내부적으로 유지하는 optional agent 목록 관련 상태다.
        supported_agents: 인스턴스가 내부적으로 유지하는 supported agent 목록 관련 상태다.
        max_feedback_rounds: 인스턴스가 내부적으로 유지하는 max 피드백 rounds 관련 상태다.
        feedback_loops: 인스턴스가 내부적으로 유지하는 피드백 루프 목록 관련 상태다.
    """
    execution_flow: list[str]
    optional_agents: list[str]
    supported_agents: list[str]
    max_feedback_rounds: int = 0
    feedback_loops: list[FeedbackLoop] = field(default_factory=list)


@dataclass(slots=True)
class ExecutionStep:
    """
    도구 계층에서 사용되는 `ExecutionStep` 클래스다.

    Attributes:
        agent: 처리 대상 agent 이름 또는 식별자다.
        label: 인스턴스가 내부적으로 유지하는 label 관련 상태다.
        phase: 인스턴스가 내부적으로 유지하는 phase 관련 상태다.
        round_number: 인스턴스가 내부적으로 유지하는 round number 관련 상태다.
    """
    agent: str
    label: str
    phase: str
    round_number: int


def normalize_agent_name(agent_name: str) -> str:
    """
    도구 계층에서 agent name을(를) 일관된 표준 형태로 정규화한다.

    주요 흐름은 `lower()`, `replace()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        agent_name: 정규화 또는 조회할 agent 이름이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return agent_name.strip().lower().replace("_", "-").replace(" ", "-")


def normalize_identifier(value: str) -> str:
    """
    도구 계층에서 식별자을(를) 일관된 표준 형태로 정규화한다.

    주요 흐름은 `normalize_agent_name()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        value: 정규화하거나 판정할 단일 값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return normalize_agent_name(value).strip("-") or "step"


def _parse_agent_list(raw_value: Any) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, agent list을(를) 해석해 구조화된 데이터로 바꾼다.

    주요 흐름은 `normalize_agent_name()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        raw_value: YAML, CLI, 환경 변수에서 읽은 원시 값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
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
    """
    모듈 내부 전용 헬퍼로, `coerce_non_negative_int()`가 맡는 non negative int 관련 작업을 수행한다.

    주요 흐름은 `isinstance()`, `max()`, `int()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        raw_value: YAML, CLI, 환경 변수에서 읽은 원시 값이다.
        default: 원시 값을 해석할 수 없을 때 사용할 기본값이다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
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
    """
    모듈 내부 전용 헬퍼로, 피드백 루프 목록을(를) 해석해 구조화된 데이터로 바꾼다.

    주요 흐름은 `normalize_agent_name()`, `_parse_agent_list()`, `normalize_identifier()`, `_coerce_non_negative_int()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        raw_value: YAML, CLI, 환경 변수에서 읽은 원시 값이다.
        default_rounds: 정수 입력값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
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
    """
    도구 계층에서 agent 실행 흐름의 최종 값을 결정한다.

    주요 흐름은 `_parse_agent_list()`, `fromkeys()`, `_coerce_non_negative_int()`, `_parse_feedback_loops()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        bundle: spec type을 키로 갖는 spec 문서 번들이다.
        rag_enabled: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        함수에서 조립한 `AgentFlow` 타입 결과다.
    """
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
    """
    도구 계층에서 실행 실행 계획을(를) 조립하거나 생성한다.

    주요 흐름은 `resolve_agent_flow()`, `setdefault()`, `ExecutionStep()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        bundle: spec type을 키로 갖는 spec 문서 번들이다.
        rag_enabled: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
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
