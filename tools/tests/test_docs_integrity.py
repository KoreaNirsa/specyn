"""
`docs integrity` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _doc_targets() -> list[Path]:
    """
    모듈 내부 전용 헬퍼로, `doc_targets()`가 맡는 targets 관련 작업을 수행한다.

    주요 흐름은 `glob()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    paths: list[Path] = [ROOT / "README.md", ROOT / "specs" / "README.md", ROOT / "tools" / "README.md"]
    paths.extend(sorted((ROOT / "docs").glob("*.md")))
    paths.extend(sorted((ROOT / "guide").glob("*.md")))
    paths.extend(sorted((ROOT / "agents").glob("*.md")))
    for name in [
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "SUPPORT.md",
        "GOVERNANCE.md",
    ]:
        paths.append(ROOT / name)
    return paths


def test_primary_docs_do_not_reference_removed_example_paths() -> None:
    """
    회귀 테스트로서 `primary_docs_do_not_reference_removed_example_paths` 시나리오를 검증한다.

    주요 흐름은 `_doc_targets()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.
    """
    for path in _doc_targets():
        text = path.read_text(encoding="utf-8")
        assert "specs/examples" not in text, path
        assert "todo-service" not in text, path


def test_primary_docs_reference_sample_service_and_templates_roles() -> None:
    """
    회귀 테스트로서 `primary_docs_reference_sample_service_and_templates_roles` 시나리오를 검증한다.

    주요 흐름은 `read_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    specs_readme = (ROOT / "specs" / "README.md").read_text(encoding="utf-8")
    assert "specs/projects/sample-service" in readme
    assert "specs/templates/" in readme
    assert "specs/projects/sample-service" in specs_readme
    assert "specs/templates/" in specs_readme


def test_markdown_links_resolve() -> None:
    """
    회귀 테스트로서 `markdown_links_resolve` 시나리오를 검증한다.

    주요 흐름은 `_doc_targets()`, `findall()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.
    """
    for path in _doc_targets():
        text = path.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if target.startswith("#"):
                continue
            resolved = (path.parent / target).resolve()
            assert resolved.exists(), f"{path}: missing link target {target}"


def test_run_flow_docs_contain_current_command_sequence() -> None:
    """
    회귀 테스트로서 `run_flow_docs_contain_current_command_sequence` 시나리오를 검증한다.

    주요 흐름은 `read_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.
    """
    targets = [
        ROOT / "README.md",
        ROOT / "docs" / "quickstart.md",
        ROOT / "docs" / "playbook.md",
        ROOT / "docs" / "cli-run-reference.md",
        ROOT / "guide" / "local-development.md",
    ]
    required_markers = [
        "python specyn.py validate --spec-dir specs/projects/sample-service",
        "compile-prompts",
        "python specyn.py run",
        "python scripts/specyn_tasks.py dev",
        "python scripts/specyn_tasks.py sample-dev",
        "http://localhost:4173",
        "http://localhost:5173",
        "http://localhost:8080/api/v1/generated/sample-service/summary",
        "http://localhost:8000/generated/sample-service/context",
    ]
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for marker in required_markers:
            assert marker in text, f"{path}: missing marker {marker}"


def test_repository_hygiene_files_do_not_contain_placeholder_github_values() -> None:
    """
    회귀 테스트로서 `repository_hygiene_files_do_not_contain_placeholder_github_values` 시나리오를 검증한다.

    주요 흐름은 `read_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    issue_config = (ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml").read_text(encoding="utf-8")
    codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "example/specyn" not in issue_config
    assert "@maintainers" not in codeowners
