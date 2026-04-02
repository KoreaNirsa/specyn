"""
여러 spec 문서를 실행 가능한 프로젝트 청사진으로 축약하는 변환 모듈이다.
문서 본문에서 엔드포인트, 예시, 시나리오, 메타데이터를 추출해 `ProjectBlueprint`와 OpenAPI/프런트엔드 계약 생성에 필요한 구조로 재배치한다.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any

from tools.agent_flow import resolve_agent_flow
from tools.spec_loader import SpecDocument

HEADING_PATTERN = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
JSON_FENCE_PATTERN = re.compile(r"```json\s*(.*?)```", re.DOTALL | re.IGNORECASE)
REQUEST_HEADING_PATTERN = re.compile(r"^###\s+.*\brequest\b", re.IGNORECASE | re.MULTILINE)
RESPONSE_HEADING_PATTERN = re.compile(r"^###\s+.*\bresponse\b", re.IGNORECASE | re.MULTILINE)
TABLE_ROW_PATTERN = re.compile(r"^\|(.+?)\|\s*$")
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9가-힣_\-]+")
PATH_VARIABLE_PATTERN = re.compile(r"\{([^{}]+)\}")


@dataclass(frozen=True)
class ApiEndpoint:
    """
    도구 계층에서 사용되는 `ApiEndpoint` 클래스다.

    Attributes:
        method: 인스턴스가 내부적으로 유지하는 method 관련 상태다.
        path: 처리 대상 경로다.
        description: 인스턴스가 내부적으로 유지하는 description 관련 상태다.
        auth: 인스턴스가 내부적으로 유지하는 인증 관련 상태다.
        note: 인스턴스가 내부적으로 유지하는 note 관련 상태다.
        operation_id: 인스턴스가 내부적으로 유지하는 operation id 관련 상태다.
        java_method_name: 인스턴스가 내부적으로 유지하는 java method name 관련 상태다.
        ts_method_name: 인스턴스가 내부적으로 유지하는 ts method name 관련 상태다.
        path_variables: 인스턴스가 내부적으로 유지하는 경로 variables 관련 상태다.
        response_status: 인스턴스가 내부적으로 유지하는 응답 상태 관련 상태다.
        request_body_allowed: 인스턴스가 내부적으로 유지하는 요청 본문 allowed 관련 상태다.
    """
    method: str
    path: str
    description: str
    auth: str
    note: str
    operation_id: str
    java_method_name: str
    ts_method_name: str
    path_variables: tuple[str, ...]
    response_status: int
    request_body_allowed: bool


@dataclass(frozen=True)
class ProjectBlueprint:
    """
    도구 계층에서 사용되는 `ProjectBlueprint` 클래스다.

    Attributes:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.
        slug: 인스턴스가 내부적으로 유지하는 슬러그 관련 상태다.
        package_slug: 인스턴스가 내부적으로 유지하는 package 슬러그 관련 상태다.
        class_name: 인스턴스가 내부적으로 유지하는 class name 관련 상태다.
        title: 인스턴스가 내부적으로 유지하는 title 관련 상태다.
        summary: 사용자에게 보여 줄 요약 문자열이다.
        scenarios: 인스턴스가 내부적으로 유지하는 scenarios 관련 상태다.
        non_functional_requirements: 인스턴스가 내부적으로 유지하는 non functional requirements 관련 상태다.
        review_rules: 인스턴스가 내부적으로 유지하는 리뷰 rules 관련 상태다.
        test_scenarios: 인스턴스가 내부적으로 유지하는 테스트 scenarios 관련 상태다.
        endpoints: 인스턴스가 내부적으로 유지하는 엔드포인트 목록 관련 상태다.
        error_policies: 인스턴스가 내부적으로 유지하는 오류 policies 관련 상태다.
        request_example: 인스턴스가 내부적으로 유지하는 요청 예시 관련 상태다.
        response_example: 인스턴스가 내부적으로 유지하는 응답 예시 관련 상태다.
        execution_flow: 인스턴스가 내부적으로 유지하는 실행 실행 흐름 관련 상태다.
        supported_agents: 인스턴스가 내부적으로 유지하는 supported agent 목록 관련 상태다.
        optional_agents: 인스턴스가 내부적으로 유지하는 optional agent 목록 관련 상태다.
        rag_enabled: 인스턴스가 내부적으로 유지하는 RAG enabled 관련 상태다.
    """
    project_id: str
    slug: str
    package_slug: str
    class_name: str
    title: str
    summary: str
    scenarios: tuple[str, ...]
    non_functional_requirements: tuple[str, ...]
    review_rules: tuple[str, ...]
    test_scenarios: tuple[str, ...]
    endpoints: tuple[ApiEndpoint, ...]
    error_policies: tuple[str, ...]
    request_example: dict[str, Any]
    response_example: dict[str, Any]
    execution_flow: tuple[str, ...]
    supported_agents: tuple[str, ...]
    optional_agents: tuple[str, ...]
    rag_enabled: bool


def normalize_slug(value: str) -> str:
    """
    도구 계층에서 슬러그을(를) 일관된 표준 형태로 정규화한다.

    주요 흐름은 `findall()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        value: 정규화하거나 판정할 단일 값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    tokens = TOKEN_PATTERN.findall(value.lower())
    slug = "-".join(token.replace("_", "-") for token in tokens if token)
    return slug.strip("-") or "sample-service"


def normalize_package_slug(value: str) -> str:
    """
    도구 계층에서 package 슬러그을(를) 일관된 표준 형태로 정규화한다.

    주요 흐름은 `normalize_slug()`, `isdigit()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        value: 정규화하거나 판정할 단일 값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    slug = normalize_slug(value).replace("-", "_")
    if slug and slug[0].isdigit():
        slug = f"project_{slug}"
    return slug or "sample_service"


def to_class_name(value: str) -> str:
    """
    도구 계층에서 `to_class_name()`가 맡는 class name 관련 작업을 수행한다.

    주요 흐름은 `split()`, `join()`, `upper()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        value: 정규화하거나 판정할 단일 값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    words = re.split(r"[^A-Za-z0-9가-힣]+", value)
    normalized = "".join(word[:1].upper() + word[1:] for word in words if word)
    return normalized or "GeneratedProject"


def _first_sentence(text: str) -> str:
    """
    모듈 내부 전용 헬퍼로, `first_sentence()`가 맡는 sentence 관련 작업을 수행한다.

    주요 흐름은 `splitlines()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        text: 파싱, 정규화, 검색 대상이 되는 문자열이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    compact = " ".join(line.strip() for line in text.splitlines() if line.strip())
    if not compact:
        return "스펙 기반 프로젝트 산출물"
    for separator in (". ", "! ", "? ", "\n"):
        if separator in compact:
            return compact.split(separator, 1)[0].strip()
    return compact[:200].strip()


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
    matches = list(HEADING_PATTERN.finditer(text))
    if not matches:
        return {}

    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[title] = text[start:end].strip()
    return sections


def _extract_bullets(text: str) -> tuple[str, ...]:
    """
    모듈 내부 전용 헬퍼로, bullets에서 필요한 정보를 추출한다.

    주요 흐름은 `splitlines()`, `match()`, `sub()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        text: 파싱, 정규화, 검색 대상이 되는 문자열이다.

    Returns:
        함수에서 조립한 `tuple[str, ...]` 타입 결과다.
    """
    bullets: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(("- ", "* ")):
            bullets.append(line[2:].strip())
        elif re.match(r"^\d+\.\s+", line):
            bullets.append(re.sub(r"^\d+\.\s+", "", line).strip())
    return tuple(item for item in bullets if item)


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
        parts = [part.strip() for part in match.group(1).split("|")]
        rows.append(parts)
    return rows


def _safe_json_load(raw: str) -> dict[str, Any]:
    """
    모듈 내부 전용 헬퍼로, `safe_json_load()`가 맡는 JSON load 관련 작업을 수행한다.

    주요 흐름은 `strip()`, `loads()`, `isinstance()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        raw: 문자열 입력값이다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    if not raw.strip():
        return {}
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {"value": loaded}


def _extract_first_json_code_block(text: str) -> dict[str, Any]:
    """
    모듈 내부 전용 헬퍼로, first JSON 코드 block에서 필요한 정보를 추출한다.

    주요 흐름은 `search()`, `_safe_json_load()`, `group()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        text: 파싱, 정규화, 검색 대상이 되는 문자열이다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    match = JSON_FENCE_PATTERN.search(text)
    if not match:
        return {}
    return _safe_json_load(match.group(1))


def _extract_json_under_heading(text: str, pattern: re.Pattern[str]) -> dict[str, Any]:
    """
    모듈 내부 전용 헬퍼로, JSON under heading에서 필요한 정보를 추출한다.

    주요 흐름은 `search()`, `end()`, `start()`, `_extract_first_json_code_block()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        text: 파싱, 정규화, 검색 대상이 되는 문자열이다.
        pattern: 문자열 검색에 사용할 정규식 패턴이다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    match = pattern.search(text)
    if not match:
        return {}
    start = match.end()
    remaining = text[start:]
    next_heading = re.search(r"^###\s+", remaining, re.MULTILINE)
    candidate = remaining[: next_heading.start()] if next_heading else remaining
    return _extract_first_json_code_block(candidate)


def _method_suffix(path: str) -> str:
    """
    모듈 내부 전용 헬퍼로, `method_suffix()`가 맡는 suffix 관련 작업을 수행한다.

    주요 흐름은 `sub()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        path: 처리 대상 경로다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    tokens = []
    for segment in path.strip("/").split("/"):
        if not segment:
            continue
        if segment.startswith("{") and segment.endswith("}"):
            tokens.append(f"by_{segment[1:-1]}")
        else:
            tokens.append(re.sub(r"[^A-Za-z0-9]+", "_", segment).strip("_"))
    return "_".join(token for token in tokens if token) or "root"


def _ts_method_name(method: str, path: str) -> str:
    """
    모듈 내부 전용 헬퍼로, `ts_method_name()`가 맡는 method name 관련 작업을 수행한다.

    주요 흐름은 `sub()`, `_method_suffix()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        method: 문자열 입력값이다.
        path: 처리 대상 경로다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return re.sub(r"_+", "_", f"{method.lower()}_{_method_suffix(path)}").strip("_")


def _java_method_name(method: str, path: str) -> str:
    """
    모듈 내부 전용 헬퍼로, `java_method_name()`가 맡는 method name 관련 작업을 수행한다.

    주요 흐름은 `_ts_method_name()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        method: 문자열 입력값이다.
        path: 처리 대상 경로다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    base = _ts_method_name(method, path)
    parts = [part for part in base.split("_") if part]
    if not parts:
        return "handleRequest"
    first, *rest = parts
    return first + "".join(part[:1].upper() + part[1:] for part in rest)


def _response_status(method: str) -> int:
    """
    모듈 내부 전용 헬퍼로, `response_status()`가 맡는 상태 관련 작업을 수행한다.

    주요 흐름은 `upper()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        method: 문자열 입력값이다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    normalized = method.upper()
    if normalized == "POST":
        return 201
    if normalized == "DELETE":
        return 204
    return 200


def _request_body_allowed(method: str) -> bool:
    """
    모듈 내부 전용 헬퍼로, `request_body_allowed()`가 맡는 본문 allowed 관련 작업을 수행한다.

    주요 흐름은 `upper()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        method: 문자열 입력값이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    return method.upper() in {"POST", "PUT", "PATCH"}


def _parse_endpoints(api_document: SpecDocument) -> tuple[ApiEndpoint, ...]:
    """
    모듈 내부 전용 헬퍼로, 엔드포인트 목록을(를) 해석해 구조화된 데이터로 바꾼다.

    주요 흐름은 `_extract_subsections()`, `_extract_markdown_table()`, `_ts_method_name()`, `ApiEndpoint()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        api_document: API 문서을(를) 나타내는 `SpecDocument` 타입 입력값이다.

    Returns:
        함수에서 조립한 `tuple[ApiEndpoint, ...]` 타입 결과다.
    """
    input_section = api_document.sections.get("입력", "")
    subsections = _extract_subsections(input_section)
    endpoint_section = subsections.get("엔드포인트", "")
    rows = _extract_markdown_table(endpoint_section)
    if len(rows) < 2:
        return tuple()

    endpoints: list[ApiEndpoint] = []
    for raw_row in rows[2:]:
        if len(raw_row) < 5:
            continue
        method, path, description, auth, note = raw_row[:5]
        if not method or method.startswith("---") or not path:
            continue
        operation_id = _ts_method_name(method, path)
        endpoints.append(
            ApiEndpoint(
                method=method.upper(),
                path=path.strip(),
                description=description.strip() or f"{method.upper()} {path.strip()}",
                auth=auth.strip() or "없음",
                note=note.strip(),
                operation_id=operation_id,
                java_method_name=_java_method_name(method, path),
                ts_method_name=operation_id,
                path_variables=tuple(PATH_VARIABLE_PATTERN.findall(path)),
                response_status=_response_status(method),
                request_body_allowed=_request_body_allowed(method),
            )
        )
    return tuple(endpoints)


def build_project_blueprint(
    *,
    project_id: str,
    bundle: dict[str, SpecDocument],
    rag_enabled: bool,
) -> ProjectBlueprint:
    """
    도구 계층에서 프로젝트 블루프린트을(를) 조립하거나 생성한다.

    주요 흐름은 `normalize_slug()`, `normalize_package_slug()`, `to_class_name()`, `_extract_subsections()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.
        bundle: spec type을 키로 갖는 spec 문서 번들이다.
        rag_enabled: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        함수에서 조립한 `ProjectBlueprint` 타입 결과다.
    """
    slug = normalize_slug(project_id)
    package_slug = normalize_package_slug(project_id)
    class_name = to_class_name(project_id)

    product_document = bundle.get("product")
    api_document = bundle.get("api")
    test_document = bundle.get("test")
    review_document = bundle.get("review")

    product_input = _extract_subsections(product_document.sections.get("입력", "")) if product_document else {}
    api_input = _extract_subsections(api_document.sections.get("입력", "")) if api_document else {}
    test_input = _extract_subsections(test_document.sections.get("입력", "")) if test_document else {}
    review_input = _extract_subsections(review_document.sections.get("입력", "")) if review_document else {}

    summary = _first_sentence(product_document.sections.get("목적", "")) if product_document else "스펙 기반 프로젝트 산출물"
    scenarios = _extract_bullets(product_input.get("핵심 시나리오", ""))
    nfr = _extract_bullets(product_input.get("비기능 요구사항", ""))
    review_rules = _extract_bullets(review_input.get("구조 규칙", ""))
    review_rules += _extract_bullets(review_input.get("보안 규칙", ""))
    test_scenarios = _extract_bullets(test_input.get("시나리오", ""))

    endpoints = _parse_endpoints(api_document) if api_document else tuple()
    error_policies = _extract_bullets(api_input.get("오류 정책", ""))

    request_examples_section = api_input.get("요청/응답 예시", "")
    request_examples_subsections = _extract_subsections(request_examples_section)
    request_example = _extract_first_json_code_block(request_examples_subsections.get("Request", ""))
    if not request_example:
        request_example = _extract_json_under_heading(request_examples_section, REQUEST_HEADING_PATTERN)
    response_example = _extract_first_json_code_block(request_examples_subsections.get("Response", ""))
    if not response_example:
        response_example = _extract_json_under_heading(request_examples_section, RESPONSE_HEADING_PATTERN)

    flow = resolve_agent_flow(bundle, rag_enabled=rag_enabled)

    return ProjectBlueprint(
        project_id=slug,
        slug=slug,
        package_slug=package_slug,
        class_name=class_name,
        title=project_id.replace("-", " ").replace("_", " ").title(),
        summary=summary,
        scenarios=scenarios,
        non_functional_requirements=nfr,
        review_rules=review_rules,
        test_scenarios=test_scenarios,
        endpoints=endpoints,
        error_policies=error_policies,
        request_example=request_example,
        response_example=response_example,
        execution_flow=tuple(flow.execution_flow),
        supported_agents=tuple(flow.supported_agents),
        optional_agents=tuple(flow.optional_agents),
        rag_enabled=rag_enabled,
    )


def blueprint_to_manifest(blueprint: ProjectBlueprint) -> dict[str, Any]:
    """
    도구 계층에서 `blueprint_to_manifest()`가 맡는 to 매니페스트 관련 작업을 수행한다.

    주요 흐름은 `list()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        blueprint: 블루프린트을(를) 나타내는 `ProjectBlueprint` 타입 입력값이다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    return {
        "projectId": blueprint.project_id,
        "title": blueprint.title,
        "summary": blueprint.summary,
        "scenarios": list(blueprint.scenarios),
        "nonFunctionalRequirements": list(blueprint.non_functional_requirements),
        "reviewRules": list(blueprint.review_rules),
        "testScenarios": list(blueprint.test_scenarios),
        "endpoints": [
            {
                "method": endpoint.method,
                "path": endpoint.path,
                "description": endpoint.description,
                "auth": endpoint.auth,
                "note": endpoint.note,
                "operationId": endpoint.operation_id,
            }
            for endpoint in blueprint.endpoints
        ],
        "errorPolicies": list(blueprint.error_policies),
        "requestExample": blueprint.request_example,
        "responseExample": blueprint.response_example,
        "executionFlow": list(blueprint.execution_flow),
        "supportedAgents": list(blueprint.supported_agents),
        "optionalAgents": list(blueprint.optional_agents),
        "ragEnabled": blueprint.rag_enabled,
    }
