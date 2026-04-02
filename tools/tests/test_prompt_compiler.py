"""
`prompt compiler` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

from pathlib import Path

from tools.prompt_compiler import compile_prompt
from tools.spec_loader import load_spec_bundle


def test_compile_prompt_contains_agent_and_specs() -> None:
    """
    회귀 테스트로서 `compile_prompt_contains_agent_and_specs` 시나리오를 검증한다.

    주요 흐름은 `load_spec_bundle()`, `compile_prompt()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    bundle = load_spec_bundle(Path("specs/projects/sample-service"))
    prompt = compile_prompt("planner", bundle, workspace_path=".workspace/sample-service")

    assert "Agent Name: planner" in prompt
    assert '<spec name="product.md" type="product">' in prompt
    assert "Execution Principles" in prompt
    assert "sample-service" in prompt
    assert "작업 관리" in prompt
