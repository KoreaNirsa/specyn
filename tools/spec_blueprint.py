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
    tokens = TOKEN_PATTERN.findall(value.lower())
    slug = "-".join(token.replace("_", "-") for token in tokens if token)
    return slug.strip("-") or "sample-service"


def normalize_package_slug(value: str) -> str:
    slug = normalize_slug(value).replace("-", "_")
    if slug and slug[0].isdigit():
        slug = f"project_{slug}"
    return slug or "sample_service"


def to_class_name(value: str) -> str:
    words = re.split(r"[^A-Za-z0-9가-힣]+", value)
    normalized = "".join(word[:1].upper() + word[1:] for word in words if word)
    return normalized or "GeneratedProject"


def _first_sentence(text: str) -> str:
    compact = " ".join(line.strip() for line in text.splitlines() if line.strip())
    if not compact:
        return "스펙 기반 프로젝트 산출물"
    for separator in (". ", "! ", "? ", "\n"):
        if separator in compact:
            return compact.split(separator, 1)[0].strip()
    return compact[:200].strip()


def _extract_subsections(text: str) -> dict[str, str]:
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
    bullets: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(("- ", "* ")):
            bullets.append(line[2:].strip())
        elif re.match(r"^\d+\.\s+", line):
            bullets.append(re.sub(r"^\d+\.\s+", "", line).strip())
    return tuple(item for item in bullets if item)


def _extract_markdown_table(text: str) -> list[list[str]]:
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
    if not raw.strip():
        return {}
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {"value": loaded}


def _extract_first_json_code_block(text: str) -> dict[str, Any]:
    match = JSON_FENCE_PATTERN.search(text)
    if not match:
        return {}
    return _safe_json_load(match.group(1))


def _extract_json_under_heading(text: str, pattern: re.Pattern[str]) -> dict[str, Any]:
    match = pattern.search(text)
    if not match:
        return {}
    start = match.end()
    remaining = text[start:]
    next_heading = re.search(r"^###\s+", remaining, re.MULTILINE)
    candidate = remaining[: next_heading.start()] if next_heading else remaining
    return _extract_first_json_code_block(candidate)


def _method_suffix(path: str) -> str:
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
    return re.sub(r"_+", "_", f"{method.lower()}_{_method_suffix(path)}").strip("_")


def _java_method_name(method: str, path: str) -> str:
    base = _ts_method_name(method, path)
    parts = [part for part in base.split("_") if part]
    if not parts:
        return "handleRequest"
    first, *rest = parts
    return first + "".join(part[:1].upper() + part[1:] for part in rest)


def _response_status(method: str) -> int:
    normalized = method.upper()
    if normalized == "POST":
        return 201
    if normalized == "DELETE":
        return 204
    return 200


def _request_body_allowed(method: str) -> bool:
    return method.upper() in {"POST", "PUT", "PATCH"}


def _parse_endpoints(api_document: SpecDocument) -> tuple[ApiEndpoint, ...]:
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
