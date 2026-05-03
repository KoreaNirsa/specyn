"""
spec markdown 파일을 읽어 front matter, 본문, 섹션 구조를 추출하는 로더 모듈이다.
여러 문서를 type 기준 딕셔너리로 묶어 상위 단계가 spec bundle을 일관된 데이터 구조로 다룰 수 있게 한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

import yaml


FRONT_MATTER_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
HEADING_PATTERN = re.compile(r"^#\s+(.+)$", re.MULTILINE)


@dataclass(slots=True)
class SpecDocument:
    """
    문서 본문과 메타데이터를 함께 보관해 후속 단계가 재해석 없이 재사용할 수 있게 하는 모델이다.

    Attributes:
        path: 처리 대상 경로다.
        name: 인스턴스가 내부적으로 유지하는 name 관련 상태다.
        spec_type: 인스턴스가 내부적으로 유지하는 spec 타입 관련 상태다.
        metadata: YAML front matter나 설정에서 읽어 온 메타데이터 딕셔너리다.
        raw_content: 인스턴스가 내부적으로 유지하는 raw content 관련 상태다.
        body: 파싱 또는 검증 대상 본문 문자열이다.
        sections: 인스턴스가 내부적으로 유지하는 섹션 목록 관련 상태다.
    """
    path: Path
    name: str
    spec_type: str
    metadata: dict[str, Any]
    raw_content: str
    body: str
    sections: dict[str, str] = field(default_factory=dict)


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """
    도구 계층에서 front matter을(를) 해석해 구조화된 데이터로 바꾼다.

    주요 흐름은 `match()`, `ValueError()`, `safe_load()`, `group()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        text: 파싱, 정규화, 검색 대상이 되는 문자열이다.

    Returns:
        함수에서 조립한 `tuple[dict[str, Any], str]` 타입 결과다.

    Raises:
        ValueError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    match = FRONT_MATTER_PATTERN.match(text)
    if not match:
        raise ValueError("YAML front matter가 없습니다.")

    metadata = yaml.safe_load(match.group(1)) or {}
    body = text[match.end() :].strip()
    return metadata, body


def extract_sections(body: str) -> dict[str, str]:
    """
    도구 계층에서 섹션 목록에서 필요한 정보를 추출한다.

    주요 흐름은 `finditer()`, `group()`, `end()`, `start()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        body: 파싱 또는 검증 대상 본문 문자열이다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    matches = list(HEADING_PATTERN.finditer(body))
    sections: dict[str, str] = {}

    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()

    return sections


def load_spec_file(path: Path) -> SpecDocument:
    """
    도구 계층에서 spec 파일을(를) 외부 소스에서 읽어 들인다.

    주요 흐름은 `parse_front_matter()`, `SpecDocument()`, `extract_sections()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        path: 처리 대상 경로다.

    Returns:
        함수에서 조립한 `SpecDocument` 타입 결과다.
    """
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_front_matter(text)
    spec_type = str(metadata.get("type") or path.stem)

    return SpecDocument(
        path=path,
        name=path.name,
        spec_type=spec_type,
        metadata=metadata,
        raw_content=text,
        body=body,
        sections=extract_sections(body),
    )


def load_spec_bundle(spec_dir: Path) -> dict[str, SpecDocument]:
    """
    도구 계층에서 spec spec 번들을(를) 외부 소스에서 읽어 들인다.

    주요 흐름은 `FileNotFoundError()`, `glob()`, `load_spec_file()`, `ValueError()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        spec_dir: spec 문서가 위치한 디렉터리다.

    Returns:
        키 기반으로 정리한 매핑 결과다.

    Raises:
        FileNotFoundError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
        ValueError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    if not spec_dir.exists():
        raise FileNotFoundError(f"spec dir not found: {spec_dir}")

    bundle: dict[str, SpecDocument] = {}
    duplicates: list[str] = []
    markdown_files = [
        path
        for path in spec_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".md"
    ]
    for path in sorted(markdown_files):
        document = load_spec_file(path)
        if document.spec_type in bundle:
            duplicates.append(document.spec_type)
            continue
        bundle[document.spec_type] = document

    if duplicates:
        duplicated = ", ".join(sorted(set(duplicates)))
        raise ValueError(f"중복 spec type이 있습니다: {duplicated}")

    return bundle
