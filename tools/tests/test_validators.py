from pathlib import Path
import shutil

from tools.spec_loader import load_spec_bundle
from tools.validators import validate_bundle


def test_example_bundle_is_valid() -> None:
    bundle = load_spec_bundle(Path("specs/examples/todo-service"))
    issues = validate_bundle(bundle)

    assert issues == []


def test_validate_bundle_fails_when_agent_definition_is_missing(
    tmp_path: Path, monkeypatch
) -> None:
    source_dir = Path("agents")
    shadow_dir = tmp_path / "agents"
    shadow_dir.mkdir()

    for source in source_dir.glob("*.md"):
        if source.name == "devops-agent.md":
            continue
        shutil.copy2(source, shadow_dir / source.name)

    monkeypatch.setattr("tools.validators.AGENTS_DIR", shadow_dir)

    bundle = load_spec_bundle(Path("specs/examples/todo-service"))
    issues = validate_bundle(bundle)

    assert any(
        issue.code == "MISSING_AGENT_DEFINITION" and "devops-agent.md" in issue.message
        for issue in issues
    )


def test_validate_bundle_fails_on_invalid_feedback_loop_order(tmp_path: Path) -> None:
    source_dir = Path("specs/examples/todo-service")
    target_dir = tmp_path / "todo-service"
    shutil.copytree(source_dir, target_dir)

    agent_path = target_dir / "agent.md"
    content = agent_path.read_text(encoding="utf-8")
    content = content.replace(
        """  - name: design-frontend-ux-sync\n    trigger_after: frontend\n    agents:\n      - design\n      - frontend\n""",
        """  - name: invalid-design-frontend-loop\n    trigger_after: design\n    agents:\n      - frontend\n""",
    )
    agent_path.write_text(content, encoding="utf-8")

    bundle = load_spec_bundle(target_dir)
    issues = validate_bundle(bundle)

    assert any(issue.code == "FEEDBACK_AGENT_ORDER_INVALID" for issue in issues)
