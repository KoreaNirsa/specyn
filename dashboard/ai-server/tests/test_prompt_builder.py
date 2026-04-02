"""
`prompt builder` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "dashboard" / "ai-server"))

from app.models.contracts import AgentExecutionRequest, SpecDocument  # noqa: E402
from app.services.prompt_builder import PromptBuilder  # noqa: E402


def test_prompt_builder_contains_spec_bundle() -> None:
    """
    회귀 테스트로서 `prompt_builder_contains_spec_bundle` 시나리오를 검증한다.

    주요 흐름은 `AgentExecutionRequest()`, `SpecDocument()`, `PromptBuilder()`, `build()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    request = AgentExecutionRequest(
        agent="API",
        projectId="sample-service",
        documents=[
            SpecDocument(
                name="api.md",
                type="api",
                content="# 목적\nTask CRUD API 생성",
            )
        ],
        previousResults=[],
        workspacePath=".workspace/sample-service",
        dryRun=True,
    )

    prompt = PromptBuilder().build(request)

    assert "프로젝트 ID: sample-service" in prompt
    assert "에이전트: api" in prompt
    assert '<spec name="api.md" type="api">' in prompt
    assert "Task CRUD API 생성" in prompt
    assert "프롬프트 안전 가드레일" in prompt
    assert "필수 출력 계약" in prompt
