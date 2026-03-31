from pathlib import Path

from tools.prompt_compiler import compile_prompt
from tools.spec_loader import load_spec_bundle


def test_compile_prompt_contains_agent_and_specs() -> None:
    bundle = load_spec_bundle(Path("specs/projects/sample-service"))
    prompt = compile_prompt("planner", bundle, workspace_path=".workspace/sample-service")

    assert "Agent Name: planner" in prompt
    assert '<spec name="product.md" type="product">' in prompt
    assert "Execution Principles" in prompt
    assert "sample-service" in prompt
    assert "작업 관리" in prompt
