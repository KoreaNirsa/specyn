import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-server"))

from app.models.contracts import AgentExecutionRequest, SpecDocument  # noqa: E402
from app.services.prompt_builder import PromptBuilder  # noqa: E402


def test_prompt_builder_contains_spec_bundle() -> None:
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
