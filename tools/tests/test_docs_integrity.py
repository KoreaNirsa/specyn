from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _doc_targets() -> list[Path]:
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
    for path in _doc_targets():
        text = path.read_text(encoding="utf-8")
        assert "specs/examples" not in text, path
        assert "todo-service" not in text, path


def test_primary_docs_reference_sample_service_and_templates_roles() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    specs_readme = (ROOT / "specs" / "README.md").read_text(encoding="utf-8")
    assert "specs/projects/sample-service" in readme
    assert "specs/templates/" in readme
    assert "specs/projects/sample-service" in specs_readme
    assert "specs/templates/" in specs_readme


def test_markdown_links_resolve() -> None:
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
    merged = "\n".join(path.read_text(encoding="utf-8") for path in targets)
    for marker in required_markers:
        assert marker in merged, f"missing marker {marker}"


def test_repository_hygiene_files_do_not_contain_placeholder_github_values() -> None:
    issue_config = (ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml").read_text(encoding="utf-8")
    codeowners = (ROOT / ".github" / "CODEOWNERS").read_text(encoding="utf-8")
    assert "example/specyn" not in issue_config
    assert "@maintainers" not in codeowners
