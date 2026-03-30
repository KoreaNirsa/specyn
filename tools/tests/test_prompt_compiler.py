from pathlib import Path

from tools.prompt_compiler import compile_prompt
from tools.spec_loader import load_spec_bundle


def test_compile_prompt_contains_agent_and_specs() -> None:
    bundle = load_spec_bundle(Path("specs/examples/todo-service"))
    prompt = compile_prompt("planner", bundle, workspace_path=".workspace/todo-service")

    assert "Agent Name: planner" in prompt
    assert '<spec name="product.md" type="product">' in prompt
    assert "Execution Principles" in prompt
    assert "Todo" in prompt
