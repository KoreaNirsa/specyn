"""
`docker ai server build` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_ai_server_dockerfile_installs_python_packages_into_virtualenv() -> None:
    """
    회귀 테스트로서 `ai_server_dockerfile_installs_python_packages_into_virtualenv` 시나리오를 검증한다.

    주요 흐름은 `read_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    content = (ROOT / "docker" / "ai-server.Dockerfile").read_text(encoding="utf-8")

    assert "VIRTUAL_ENV=/opt/specyn-venv" in content
    assert 'PATH=/opt/specyn-venv/bin:${PATH}' in content
    assert 'python -m venv "${VIRTUAL_ENV}"' in content
    assert "projects/sample-service/ai-server/requirements.txt" not in content


def test_env_example_uses_danger_full_access_for_docker_codex() -> None:
    """
    회귀 테스트로서 `env_example_uses_danger_full_access_for_docker_codex` 시나리오를 검증한다.

    주요 흐름은 `read_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    content = (ROOT / ".env.example").read_text(encoding="utf-8")

    assert "--sandbox danger-full-access" in content
