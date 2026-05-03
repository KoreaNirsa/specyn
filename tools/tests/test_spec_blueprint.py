from pathlib import Path

from tools.spec_blueprint import build_project_blueprint
from tools.spec_loader import load_spec_bundle


def test_build_project_blueprint_extracts_endpoint_and_examples() -> None:
    bundle = load_spec_bundle(Path("specs/001-sample-service"))

    blueprint = build_project_blueprint(
        project_id="sample-service",
        bundle=bundle,
        rag_enabled=False,
    )

    assert blueprint.slug == "sample-service"
    assert blueprint.package_slug == "sample_service"
    assert len(blueprint.endpoints) == 5
    assert blueprint.endpoints[0].path == "/api/v1/tasks"
    assert blueprint.request_example["title"] == "Write CI workflow"
    assert blueprint.response_example["status"] == "PENDING"
    assert blueprint.execution_flow[0] == "planner"
