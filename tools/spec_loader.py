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
    path: Path
    name: str
    spec_type: str
    metadata: dict[str, Any]
    raw_content: str
    body: str
    sections: dict[str, str] = field(default_factory=dict)


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONT_MATTER_PATTERN.match(text)
    if not match:
        raise ValueError("YAML front matter가 없습니다.")

    metadata = yaml.safe_load(match.group(1)) or {}
    body = text[match.end() :].strip()
    return metadata, body


def extract_sections(body: str) -> dict[str, str]:
    matches = list(HEADING_PATTERN.finditer(body))
    sections: dict[str, str] = {}

    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()

    return sections


def load_spec_file(path: Path) -> SpecDocument:
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
    if not spec_dir.exists():
        raise FileNotFoundError(f"spec dir not found: {spec_dir}")

    bundle: dict[str, SpecDocument] = {}
    duplicates: list[str] = []
    for path in sorted(spec_dir.glob("*.md")):
        document = load_spec_file(path)
        if document.spec_type in bundle:
            duplicates.append(document.spec_type)
            continue
        bundle[document.spec_type] = document

    if duplicates:
        duplicated = ", ".join(sorted(set(duplicates)))
        raise ValueError(f"중복 spec type이 있습니다: {duplicated}")

    return bundle
