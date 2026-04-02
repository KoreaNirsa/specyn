"""
Regression tests for prompt builder output.
"""

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "dashboard" / "ai-server"))

from app.models.contracts import AgentExecutionRequest, SpecDocument  # noqa: E402
from app.services.prompt_builder import PromptBuilder  # noqa: E402


def test_prompt_builder_contains_spec_bundle() -> None:
    """
    Prompt output should include the key runtime contract sections and spec bundle.
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

    assert "Project ID: sample-service" in prompt
    assert "Agent: api" in prompt
    assert '<spec name="api.md" type="api">' in prompt
    assert "Task CRUD API 생성" in prompt
    assert "[Execution Guardrails]" in prompt
    assert "[Required Output Contract]" in prompt
    assert "docker-compose.local.yml" in prompt
    assert "compose.yaml" in prompt
