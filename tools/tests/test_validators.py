"""
`validators` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

from pathlib import Path
import shutil

from tools.spec_loader import load_spec_bundle
from tools.validators import validate_bundle


def test_sample_service_bundle_is_valid() -> None:
    """
    회귀 테스트로서 `sample_service_bundle_is_valid` 시나리오를 검증한다.

    주요 흐름은 `load_spec_bundle()`, `validate_bundle()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    bundle = load_spec_bundle(Path("specs/projects/sample-service"))
    issues = validate_bundle(bundle)

    assert issues == []


def test_validate_bundle_fails_when_agent_definition_is_missing(
    tmp_path: Path, monkeypatch
) -> None:
    """
    회귀 테스트로서 `validate_bundle_fails_when_agent_definition_is_missing` 시나리오를 검증한다.

    주요 흐름은 `glob()`, `copy2()`, `load_spec_bundle()`, `validate_bundle()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        tmp_path: 파일 시스템 경로 객체다.
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
    """
    source_dir = Path("agents")
    shadow_dir = tmp_path / "agents"
    shadow_dir.mkdir()

    for source in source_dir.glob("*.md"):
        if source.name == "devops-agent.md":
            continue
        shutil.copy2(source, shadow_dir / source.name)

    monkeypatch.setattr("tools.validators.AGENTS_DIR", shadow_dir)

    bundle = load_spec_bundle(Path("specs/projects/sample-service"))
    issues = validate_bundle(bundle)

    assert any(
        issue.code == "MISSING_AGENT_DEFINITION" and "devops-agent.md" in issue.message
        for issue in issues
    )


def test_validate_bundle_fails_on_invalid_feedback_loop_order(tmp_path: Path) -> None:
    """
    회귀 테스트로서 `validate_bundle_fails_on_invalid_feedback_loop_order` 시나리오를 검증한다.

    주요 흐름은 `copytree()`, `load_spec_bundle()`, `validate_bundle()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        tmp_path: 파일 시스템 경로 객체다.
    """
    source_dir = Path("specs/projects/sample-service")
    target_dir = tmp_path / "sample-service"
    shutil.copytree(source_dir, target_dir)

    agent_path = target_dir / "agent.md"
    content = agent_path.read_text(encoding="utf-8")
    content = content.replace(
        """  - name: design-frontend-ux-sync
    trigger_after: frontend
    agents:
      - design
      - frontend
""",
        """  - name: invalid-design-frontend-loop
    trigger_after: design
    agents:
      - frontend
""",
    )
    agent_path.write_text(content, encoding="utf-8")

    bundle = load_spec_bundle(target_dir)
    issues = validate_bundle(bundle)

    assert any(issue.code == "FEEDBACK_AGENT_ORDER_INVALID" for issue in issues)
