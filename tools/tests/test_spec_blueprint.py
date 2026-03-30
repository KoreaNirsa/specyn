from pathlib import Path

from tools.spec_blueprint import build_project_blueprint
from tools.spec_loader import load_spec_bundle


def test_build_project_blueprint_extracts_endpoint_and_examples() -> None:
    bundle = load_spec_bundle(Path("specs/examples/todo-service"))

    blueprint = build_project_blueprint(
        project_id="todo-service",
        bundle=bundle,
        rag_enabled=False,
    )

    assert blueprint.slug == "todo-service"
    assert blueprint.package_slug == "todo_service"
    assert len(blueprint.endpoints) == 5
    assert blueprint.endpoints[0].path == "/api/v1/todos"
    assert blueprint.request_example["title"] == "문서 작성"
    assert blueprint.response_example["status"] == "PENDING"
    assert blueprint.execution_flow[0] == "planner"
