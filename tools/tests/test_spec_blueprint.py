"""
`spec blueprint` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

from pathlib import Path

from tools.spec_blueprint import build_project_blueprint
from tools.spec_loader import load_spec_bundle


def test_build_project_blueprint_extracts_endpoint_and_examples() -> None:
    """
    회귀 테스트로서 `build_project_blueprint_extracts_endpoint_and_examples` 시나리오를 검증한다.

    주요 흐름은 `load_spec_bundle()`, `build_project_blueprint()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    bundle = load_spec_bundle(Path("specs/projects/sample-service"))

    blueprint = build_project_blueprint(
        project_id="sample-service",
        bundle=bundle,
        rag_enabled=False,
    )

    assert blueprint.slug == "sample-service"
    assert blueprint.package_slug == "sample_service"
    assert len(blueprint.endpoints) == 5
    assert blueprint.endpoints[0].path == "/api/v1/tasks"
    assert blueprint.request_example["title"] == "README 업데이트"
    assert blueprint.response_example["items"][0]["status"] == "PENDING"
    assert blueprint.execution_flow[0] == "planner"
