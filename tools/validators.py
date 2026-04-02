"""
spec 문서와 spec bundle 전체를 계약에 맞춰 검증하는 정적 검사 모듈이다.
문서 단위 형상 검증과 번들 단위 의존성·agent flow·feedback metadata 검증을 나눠 수행해, 실행 전에 구조적 오류를 가능한 빨리 드러내는 역할을 한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
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
SUBSECTION_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
TABLE_ROW_PATTERN = re.compile(r"^\|(.+?)\|\s*$")
REQUEST_HEADING_PATTERN = re.compile(r"^###\s+.*\brequest\b", re.IGNORECASE | re.MULTILINE)
RESPONSE_HEADING_PATTERN = re.compile(r"^###\s+.*\bresponse\b", re.IGNORECASE | re.MULTILINE)


@dataclass(slots=True)
class ValidationIssue:
    """
    검증 단계에서 발견된 문제를 코드와 메시지로 표현하는 데이터 모델이다.

    Attributes:
        level: 인스턴스가 내부적으로 유지하는 level 관련 상태다.
        code: 종료 코드나 상태 코드 값이다.
        message: 출력하거나 전달할 메시지 문자열이다.
    """
    level: str
    code: str
    message: str


def agent_definition_path(agent_name: str) -> Path:
    """
    도구 계층에서 `agent_definition_path()`가 맡는 정의 경로 관련 작업을 수행한다.

    주요 흐름은 `normalize_agent_name()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        agent_name: 정규화 또는 조회할 agent 이름이다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    normalized = normalize_agent_name(agent_name)
    return AGENTS_DIR / f"{normalized}-agent.md"


def _is_non_negative_int(value: Any) -> bool:
    """
    모듈 내부 전용 헬퍼로, non negative int 여부를 판단한다.

    주요 흐름은 `isinstance()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        value: 정규화하거나 판정할 단일 값이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _extract_subsections(text: str) -> dict[str, str]:
    """
    모듈 내부 전용 헬퍼로, 하위 섹션에서 필요한 정보를 추출한다.

    주요 흐름은 `finditer()`, `group()`, `end()`, `start()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        text: 파싱, 정규화, 검색 대상이 되는 문자열이다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    matches = list(SUBSECTION_PATTERN.finditer(text))
    if not matches:
        return {}
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[title] = text[start:end].strip()
    return sections


def _extract_bullets(text: str) -> list[str]:
    """
    모듈 내부 전용 헬퍼로, bullets에서 필요한 정보를 추출한다.

    주요 흐름은 `splitlines()`, `match()`, `sub()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        text: 파싱, 정규화, 검색 대상이 되는 문자열이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    items: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(("- ", "* ")):
            items.append(line[2:].strip())
        elif re.match(r"^\d+\.\s+", line):
            items.append(re.sub(r"^\d+\.\s+", "", line).strip())
    return [item for item in items if item]


def _extract_markdown_table(text: str) -> list[list[str]]:
    """
    모듈 내부 전용 헬퍼로, Markdown 표에서 필요한 정보를 추출한다.

    주요 흐름은 `splitlines()`, `match()`, `group()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        text: 파싱, 정규화, 검색 대상이 되는 문자열이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    rows: list[list[str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            if rows:
                break
            continue
        match = TABLE_ROW_PATTERN.match(line)
        if not match:
            continue
        rows.append([part.strip() for part in match.group(1).split("|")])
    return rows


def _validate_product_shape(document: SpecDocument) -> list[ValidationIssue]:
    """
    모듈 내부 전용 헬퍼로, 제품 spec shape이(가) 계약을 만족하는지 검증한다.

    주요 흐름은 `_extract_subsections()`, `_extract_bullets()`, `ValidationIssue()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        document: 검증 또는 파싱 대상 spec 문서 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    issues: list[ValidationIssue] = []
    subsections = _extract_subsections(document.sections.get("입력", ""))
    scenarios = _extract_bullets(subsections.get("핵심 시나리오", ""))
    nfr = _extract_bullets(subsections.get("비기능 요구사항", ""))
    excluded = _extract_bullets(subsections.get("제외 범위", ""))

    if len(scenarios) < 3:
        issues.append(ValidationIssue("ERROR", "INSUFFICIENT_PRODUCT_SCENARIOS", f"{document.name}: 핵심 시나리오는 3개 이상이어야 합니다."))
    if len(nfr) < 4:
        issues.append(ValidationIssue("ERROR", "INSUFFICIENT_NFRS", f"{document.name}: 비기능 요구사항은 4개 이상이어야 합니다."))
    if not excluded:
        issues.append(ValidationIssue("ERROR", "MISSING_EXCLUDED_SCOPE", f"{document.name}: 제외 범위가 비어 있습니다."))
    return issues


def _validate_api_shape(document: SpecDocument) -> list[ValidationIssue]:
    """
    모듈 내부 전용 헬퍼로, API shape이(가) 계약을 만족하는지 검증한다.

    주요 흐름은 `_extract_subsections()`, `_extract_markdown_table()`, `ValidationIssue()`, `search()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        document: 검증 또는 파싱 대상 spec 문서 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    issues: list[ValidationIssue] = []
    subsections = _extract_subsections(document.sections.get("입력", ""))
    endpoint_table = _extract_markdown_table(subsections.get("엔드포인트", ""))
    endpoint_rows = [row for row in endpoint_table[2:] if len(row) >= 5 and row[0] and not row[0].startswith("---")]
    if not endpoint_rows:
        issues.append(ValidationIssue("ERROR", "MISSING_ENDPOINT_ROWS", f"{document.name}: 엔드포인트 표에 최소 1개 이상의 endpoint가 있어야 합니다."))
    request_response_section = subsections.get("요청/응답 예시", "")
    has_request = bool(REQUEST_HEADING_PATTERN.search(request_response_section))
    has_response = bool(RESPONSE_HEADING_PATTERN.search(request_response_section))
    if not (has_request and has_response):
        issues.append(ValidationIssue("ERROR", "MISSING_REQUEST_RESPONSE_EXAMPLES", f"{document.name}: 요청/응답 예시는 Request/Response 하위 섹션을 모두 포함해야 합니다."))
    if not _extract_bullets(subsections.get("오류 정책", "")):
        issues.append(ValidationIssue("ERROR", "MISSING_ERROR_POLICY", f"{document.name}: 오류 정책이 비어 있습니다."))
    return issues


def _validate_test_shape(document: SpecDocument) -> list[ValidationIssue]:
    """
    모듈 내부 전용 헬퍼로, 테스트 shape이(가) 계약을 만족하는지 검증한다.

    주요 흐름은 `_extract_bullets()`, `_extract_subsections()`, `ValidationIssue()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        document: 검증 또는 파싱 대상 spec 문서 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    scenarios = _extract_bullets(_extract_subsections(document.sections.get("입력", "")).get("시나리오", ""))
    if len(scenarios) < 4:
        return [ValidationIssue("ERROR", "INSUFFICIENT_TEST_SCENARIOS", f"{document.name}: 테스트 시나리오는 4개 이상이어야 합니다.")]
    return []


def _validate_review_shape(document: SpecDocument) -> list[ValidationIssue]:
    """
    모듈 내부 전용 헬퍼로, 리뷰 shape이(가) 계약을 만족하는지 검증한다.

    주요 흐름은 `_extract_subsections()`, `_extract_bullets()`, `ValidationIssue()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        document: 검증 또는 파싱 대상 spec 문서 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    subsections = _extract_subsections(document.sections.get("입력", ""))
    rules = (
        _extract_bullets(subsections.get("구조 규칙", ""))
        + _extract_bullets(subsections.get("보안 규칙", ""))
        + _extract_bullets(subsections.get("테스트 규칙", ""))
        + _extract_bullets(subsections.get("운영 규칙", ""))
    )
    if len(rules) < 4:
        return [ValidationIssue("ERROR", "INSUFFICIENT_REVIEW_RULES", f"{document.name}: review 체크리스트를 4개 이상 명시해야 합니다.")]
    return []


def validate_document(document: SpecDocument) -> list[ValidationIssue]:
    """
    도구 계층에서 문서이(가) 계약을 만족하는지 검증한다.

    주요 흐름은 `keys()`, `ValidationIssue()`, `normalize_agent_name()`, `_validate_product_shape()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        document: 검증 또는 파싱 대상 spec 문서 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    issues: list[ValidationIssue] = []
    missing_sections = REQUIRED_SECTIONS - set(document.sections.keys())
    for section in sorted(missing_sections):
        issues.append(ValidationIssue("ERROR", "MISSING_SECTION", f"{document.name}: '{section}' 섹션이 없습니다."))

    required_meta = {"id", "type", "version", "owner_agent", "status", "depends_on"}
    missing_meta = required_meta - set(document.metadata.keys())
    for key in sorted(missing_meta):
        issues.append(ValidationIssue("ERROR", "MISSING_METADATA", f"{document.name}: '{key}' 메타데이터가 없습니다."))

    owner_agent = document.metadata.get("owner_agent")
    if owner_agent is not None:
        normalized_owner = normalize_agent_name(str(owner_agent))
        if normalized_owner not in KNOWN_AGENT_NAMES:
            issues.append(ValidationIssue("ERROR", "UNKNOWN_OWNER_AGENT", f"{document.name}: 지원하지 않는 owner_agent='{owner_agent}' 입니다."))

    depends_on = document.metadata.get("depends_on")
    if depends_on is not None and not isinstance(depends_on, list):
        issues.append(ValidationIssue("ERROR", "INVALID_METADATA_TYPE", f"{document.name}: 'depends_on'은 배열이어야 합니다."))

    prompt_section = document.sections.get("Prompt")
    if prompt_section:
        missing_prompt_subsections = [title for title in sorted(REQUIRED_PROMPT_SUBSECTIONS) if f"## {title}" not in prompt_section and f"### {title}" not in prompt_section]
        for title in missing_prompt_subsections:
            issues.append(ValidationIssue("ERROR", "MISSING_PROMPT_SUBSECTION", f"{document.name}: Prompt 섹션에 '{title}' 하위 섹션이 없습니다."))

    if document.spec_type == "product":
        issues.extend(_validate_product_shape(document))
    elif document.spec_type == "api":
        issues.extend(_validate_api_shape(document))
    elif document.spec_type == "test":
        issues.extend(_validate_test_shape(document))
    elif document.spec_type == "review":
        issues.extend(_validate_review_shape(document))
    return issues


def _validate_spec_dependencies(bundle: dict[str, SpecDocument]) -> list[ValidationIssue]:
    """
    모듈 내부 전용 헬퍼로, spec dependencies이(가) 계약을 만족하는지 검증한다.

    주요 흐름은 `ValidationIssue()`, `visit()`, `remove()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        bundle: spec type을 키로 갖는 spec 문서 번들이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    issues: list[ValidationIssue] = []
    for document in bundle.values():
        depends_on = document.metadata.get("depends_on") or []
        if not isinstance(depends_on, list):
            continue
        for dependency in depends_on:
            dependency_name = str(dependency)
            if dependency_name not in bundle:
                issues.append(ValidationIssue("ERROR", "UNKNOWN_SPEC_DEPENDENCY", f"{document.name}: depends_on에 선언된 '{dependency_name}' spec가 bundle에 없습니다."))

    temp_marks: set[str] = set()
    perm_marks: set[str] = set()

    def visit(spec_type: str) -> None:
        """
        도구 계층에서 `visit()`가 맡는 작업 관련 작업을 수행한다.

        주요 흐름은 `ValidationIssue()`, `visit()`, `remove()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Args:
            spec_type: 문자열 입력값이다.
        """
        if spec_type in perm_marks:
            return
        if spec_type in temp_marks:
            issues.append(ValidationIssue("ERROR", "SPEC_DEPENDENCY_CYCLE", f"spec dependency cycle이 감지되었습니다: '{spec_type}'"))
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
    """
    모듈 내부 전용 헬퍼로, agent 정의 목록이(가) 계약을 만족하는지 검증한다.

    주요 흐름은 `agent_definition_path()`, `ValidationIssue()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        agent_names: agent names을(를) 나타내는 `set[str]` 타입 입력값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    issues: list[ValidationIssue] = []
    for agent_name in sorted(agent_names):
        definition_path = agent_definition_path(agent_name)
        if not definition_path.exists():
            issues.append(ValidationIssue("ERROR", "MISSING_AGENT_DEFINITION", f"agent.md: agent 정의 문서가 없습니다. expected='{definition_path.relative_to(AGENTS_DIR.parent)}'"))
    return issues


def _validate_feedback_metadata(*, agent_document: SpecDocument, execution_flow: list[str], optional_agents: list[str], supported_agents: list[str]) -> list[ValidationIssue]:
    """
    모듈 내부 전용 헬퍼로, 피드백 메타데이터이(가) 계약을 만족하는지 검증한다.

    주요 흐름은 `_is_non_negative_int()`, `ValidationIssue()`, `normalize_agent_name()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        agent_document: agent 문서을(를) 나타내는 `SpecDocument` 타입 입력값이다.
        execution_flow: 순서를 유지하는 목록 입력값이다.
        optional_agents: 순서를 유지하는 목록 입력값이다.
        supported_agents: 순서를 유지하는 목록 입력값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    issues: list[ValidationIssue] = []
    metadata = agent_document.metadata
    max_feedback_rounds = metadata.get("max_feedback_rounds")
    if max_feedback_rounds is not None and not _is_non_negative_int(max_feedback_rounds):
        issues.append(ValidationIssue("ERROR", "INVALID_MAX_FEEDBACK_ROUNDS", "agent.md: max_feedback_rounds는 0 이상의 정수여야 합니다."))

    raw_feedback_loops = metadata.get("feedback_loops")
    if raw_feedback_loops is None:
        return issues
    if not isinstance(raw_feedback_loops, list):
        issues.append(ValidationIssue("ERROR", "INVALID_FEEDBACK_LOOPS_TYPE", "agent.md: feedback_loops는 배열이어야 합니다."))
        return issues

    execution_index = {agent_name: index for index, agent_name in enumerate(execution_flow)}
    supported_set = set(supported_agents) | set(optional_agents) | set(execution_flow)
    for index, loop in enumerate(raw_feedback_loops, start=1):
        prefix = f"agent.md: feedback_loops[{index}]"
        if not isinstance(loop, dict):
            issues.append(ValidationIssue("ERROR", "INVALID_FEEDBACK_LOOP", f"{prefix}는 객체여야 합니다."))
            continue

        trigger_after_raw = loop.get("trigger_after")
        trigger_after = normalize_agent_name(str(trigger_after_raw)) if trigger_after_raw is not None else ""
        if not trigger_after:
            issues.append(ValidationIssue("ERROR", "MISSING_FEEDBACK_TRIGGER", f"{prefix}: trigger_after가 필요합니다."))
        elif trigger_after not in KNOWN_AGENT_NAMES:
            issues.append(ValidationIssue("ERROR", "UNKNOWN_AGENT", f"{prefix}: 지원하지 않는 trigger_after agent '{trigger_after}' 입니다."))
        elif trigger_after not in execution_index:
            issues.append(ValidationIssue("ERROR", "FEEDBACK_TRIGGER_NOT_IN_FLOW", f"{prefix}: trigger_after '{trigger_after}' 는 execution_flow에 포함되어야 합니다."))

        agents_raw = loop.get("agents")
        if not isinstance(agents_raw, list) or not agents_raw:
            issues.append(ValidationIssue("ERROR", "INVALID_FEEDBACK_LOOP_AGENTS", f"{prefix}: agents는 비어 있지 않은 배열이어야 합니다."))
            normalized_agents: list[str] = []
        else:
            normalized_agents = [normalize_agent_name(str(agent_name)) for agent_name in agents_raw if str(agent_name).strip()]
            if not normalized_agents:
                issues.append(ValidationIssue("ERROR", "INVALID_FEEDBACK_LOOP_AGENTS", f"{prefix}: agents에 유효한 agent 이름이 없습니다."))
            if len(set(normalized_agents)) != len(normalized_agents):
                issues.append(ValidationIssue("ERROR", "DUPLICATED_AGENT_IN_FEEDBACK_LOOP", f"{prefix}: agents에 중복 agent가 있습니다."))

        max_rounds = loop.get("max_rounds")
        if max_rounds is not None and not _is_non_negative_int(max_rounds):
            issues.append(ValidationIssue("ERROR", "INVALID_FEEDBACK_LOOP_MAX_ROUNDS", f"{prefix}: max_rounds는 0 이상의 정수여야 합니다."))

        if trigger_after in execution_index:
            trigger_index = execution_index[trigger_after]
            for agent_name in normalized_agents:
                if agent_name not in KNOWN_AGENT_NAMES:
                    issues.append(ValidationIssue("ERROR", "UNKNOWN_AGENT", f"{prefix}: 지원하지 않는 agent '{agent_name}' 입니다."))
                    continue
                if agent_name not in supported_set:
                    issues.append(ValidationIssue("ERROR", "FEEDBACK_AGENT_NOT_SUPPORTED", f"{prefix}: feedback agent '{agent_name}' 는 supported_agents 또는 execution_flow에 포함되어야 합니다."))
                    continue
                if agent_name not in execution_index:
                    issues.append(ValidationIssue("ERROR", "FEEDBACK_AGENT_NOT_IN_FLOW", f"{prefix}: feedback agent '{agent_name}' 는 execution_flow에 포함되어야 합니다."))
                    continue
                if execution_index[agent_name] > trigger_index:
                    issues.append(ValidationIssue("ERROR", "FEEDBACK_AGENT_ORDER_INVALID", f"{prefix}: feedback agent '{agent_name}' 는 trigger_after '{trigger_after}' 이전 또는 동일 시점에 있어야 합니다."))
    return issues


def _validate_agent_flow(bundle: dict[str, SpecDocument]) -> list[ValidationIssue]:
    """
    모듈 내부 전용 헬퍼로, agent 실행 흐름이(가) 계약을 만족하는지 검증한다.

    주요 흐름은 `resolve_agent_flow()`, `ValidationIssue()`, `_validate_feedback_metadata()`, `_validate_agent_definitions()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        bundle: spec type을 키로 갖는 spec 문서 번들이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    issues: list[ValidationIssue] = []
    agent_document = bundle.get("agent")
    if agent_document is None:
        return issues
    flow = resolve_agent_flow(bundle, rag_enabled=False)
    execution_flow = flow.execution_flow
    optional_agents = flow.optional_agents
    supported_agents = flow.supported_agents
    if not execution_flow:
        issues.append(ValidationIssue("ERROR", "EMPTY_AGENT_FLOW", "agent.md: execution_flow가 비어 있습니다."))
        return issues

    seen: set[str] = set()
    for agent_name in execution_flow:
        if agent_name not in KNOWN_AGENT_NAMES:
            issues.append(ValidationIssue("ERROR", "UNKNOWN_AGENT", f"agent.md: 지원하지 않는 agent '{agent_name}' 이(가) execution_flow에 있습니다."))
        if agent_name in seen:
            issues.append(ValidationIssue("ERROR", "DUPLICATED_AGENT_IN_FLOW", f"agent.md: execution_flow에 '{agent_name}' 가 중복 선언되었습니다."))
        seen.add(agent_name)

    missing_required_agents = REQUIRED_FLOW_AGENTS - set(execution_flow)
    for agent_name in sorted(missing_required_agents):
        issues.append(ValidationIssue("ERROR", "MISSING_REQUIRED_AGENT", f"agent.md: execution_flow에 필수 agent '{agent_name}' 이(가) 없습니다."))

    for collection_name, values in {"optional_agents": optional_agents, "supported_agents": supported_agents}.items():
        for agent_name in values:
            if agent_name not in KNOWN_AGENT_NAMES:
                issues.append(ValidationIssue("ERROR", "UNKNOWN_AGENT", f"agent.md: {collection_name}에 지원하지 않는 agent '{agent_name}' 이(가) 있습니다."))

    if supported_agents:
        for agent_name in [agent for agent in execution_flow if agent not in supported_agents]:
            issues.append(ValidationIssue("ERROR", "FLOW_NOT_IN_SUPPORTED_AGENTS", f"agent.md: execution_flow의 '{agent_name}' 는 supported_agents에 포함되어야 합니다."))
        for agent_name in [agent for agent in optional_agents if agent not in supported_agents]:
            issues.append(ValidationIssue("ERROR", "OPTIONAL_AGENT_NOT_IN_SUPPORTED_AGENTS", f"agent.md: optional_agents의 '{agent_name}' 는 supported_agents에 포함되어야 합니다."))

    issues.extend(_validate_feedback_metadata(agent_document=agent_document, execution_flow=execution_flow, optional_agents=optional_agents, supported_agents=supported_agents))
    referenced_agents = set(execution_flow) | set(optional_agents) | set(supported_agents)
    for loop in flow.feedback_loops:
        referenced_agents.update(loop.agents)
        if loop.trigger_after:
            referenced_agents.add(loop.trigger_after)
    issues.extend(_validate_agent_definitions(referenced_agents))
    return issues


def validate_bundle(bundle: dict[str, SpecDocument]) -> list[ValidationIssue]:
    """
    도구 계층에서 spec 번들이(가) 계약을 만족하는지 검증한다.

    주요 흐름은 `keys()`, `ValidationIssue()`, `validate_document()`, `_validate_spec_dependencies()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        bundle: spec type을 키로 갖는 spec 문서 번들이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    issues: list[ValidationIssue] = []
    missing_types = REQUIRED_SPEC_TYPES - set(bundle.keys())
    for spec_type in sorted(missing_types):
        issues.append(ValidationIssue("ERROR", "MISSING_SPEC", f"필수 spec '{spec_type}' 이(가) 없습니다."))
    for document in bundle.values():
        issues.extend(validate_document(document))
    issues.extend(_validate_spec_dependencies(bundle))
    issues.extend(_validate_agent_flow(bundle))
    return issues
