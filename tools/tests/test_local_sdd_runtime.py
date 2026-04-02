from __future__ import annotations

import json
import py_compile
from pathlib import Path

import yaml

from tools import local_sdd_runtime, prompt_compiler
from tools.local_sdd_runtime import LocalSddRuntime
from tools.spec_loader import load_spec_bundle


def test_local_runtime_generates_repo_artifacts(monkeypatch, tmp_path: Path) -> None:
    bundle = load_spec_bundle(Path("specs/projects/sample-service"))

    monkeypatch.setattr(prompt_compiler, "AGENT_DIR", Path("agents"))
    monkeypatch.setattr(local_sdd_runtime, "PROMPT_ROOT_DIR", tmp_path / ".specyn" / "prompts")
    monkeypatch.setattr(local_sdd_runtime, "GENERATED_DOCS_DIR", Path("docs") / "generated")
    monkeypatch.setattr(local_sdd_runtime, "GENERATED_AI_SERVER_DIR", Path("ai-server") / "app" / "generated")

    runtime = LocalSddRuntime(output_root=tmp_path)
    result = runtime.execute(
        project_id="sample-service",
        bundle=bundle,
        workspace_path=".workspace/sample-service",
        rag_enabled=False,
        runtime_mode="local",
    )

    assert result.status == "BLOCKED"
    assert result.generated_files

    frontend_package = tmp_path / "frontend" / "package.json"
    frontend_entry = tmp_path / "frontend" / "src" / "App.tsx"
    frontend_contract = tmp_path / "frontend" / "src" / "generated" / "sample-service" / "apiContract.ts"
    frontend_page = tmp_path / "frontend" / "src" / "generated" / "sample-service" / "GeneratedProjectPage.tsx"
    backend_build = tmp_path / "backend" / "build.gradle.kts"
    backend_application = tmp_path / "backend" / "src" / "main" / "resources" / "application.yml"
    backend_controller = (
        tmp_path
        / "backend"
        / "src"
        / "main"
        / "java"
        / "com"
        / "axbuilder"
        / "backend"
        / "generated"
        / "sample_service"
        / "GeneratedSampleServiceController.java"
    )
    ai_main = tmp_path / "ai-server" / "app" / "main.py"
    ai_config = tmp_path / "ai-server" / "app" / "core" / "config.py"
    ai_router = tmp_path / "ai-server" / "app" / "generated" / "sample_service" / "router.py"
    generated_doc = tmp_path / "docs" / "generated" / "sample-service.md"
    openapi_doc = tmp_path / "docs" / "openapi" / "sample-service.yaml"
    run_manifest = result.workspace_dir / ".specyn" / "runs" / result.run_id / "manifest.json"

    for path in [
        frontend_package,
        frontend_entry,
        frontend_contract,
        frontend_page,
        backend_build,
        backend_application,
        backend_controller,
        ai_main,
        ai_config,
        ai_router,
        generated_doc,
        openapi_doc,
        run_manifest,
    ]:
        assert path.exists(), path

    frontend_page_text = frontend_page.read_text(encoding="utf-8")
    assert "Generated CRUD Demo" in frontend_page_text
    assert 'const TASKS_URL = BACKEND_URL + "/api/v1/tasks";' in frontend_page_text
    assert "Generated Summary" in frontend_page_text
    assert "API Contract" in frontend_page_text
    assert 'requestNoContent(taskDetailUrl(taskId), { method: "DELETE" })' in frontend_page_text

    backend_controller_text = backend_controller.read_text(encoding="utf-8")
    assert 'private final AtomicLong sequence = new AtomicLong(0);' in backend_controller_text
    assert '@GetMapping("/api/v1/tasks")' in backend_controller_text
    assert '@PatchMapping("/api/v1/tasks/{id}/status")' in backend_controller_text
    assert '@DeleteMapping("/api/v1/tasks/{id}")' in backend_controller_text
    assert 'errorPayload("VALIDATION_ERROR"' in backend_controller_text

    ai_router_text = ai_router.read_text(encoding="utf-8")
    assert "GENERATED_MANIFEST" in ai_router_text
    py_compile.compile(str(ai_router), doraise=True)

    generated_doc_text = generated_doc.read_text(encoding="utf-8")
    assert "sample-service" in generated_doc_text
    assert "python scripts/specyn_tasks.py sample-dev" in generated_doc_text
    assert "http://localhost:5173" in generated_doc_text

    frontend_package_text = frontend_package.read_text(encoding="utf-8")
    assert "specyn-sample-service-frontend" in frontend_package_text

    backend_application_text = backend_application.read_text(encoding="utf-8")
    assert "SERVER_PORT:8080" in backend_application_text
    assert "http://localhost:8000" in backend_application_text

    ai_config_text = ai_config.read_text(encoding="utf-8")
    assert "http://localhost:5173" in ai_config_text
    assert "parents[3]" in ai_config_text

    openapi_payload = yaml.safe_load(openapi_doc.read_text(encoding="utf-8"))
    assert openapi_payload["openapi"] == "3.1.0"
    assert "/api/v1/tasks" in openapi_payload["paths"]
    assert "get" in openapi_payload["paths"]["/api/v1/tasks"]
    assert "post" in openapi_payload["paths"]["/api/v1/tasks"]
    assert openapi_payload["paths"]["/api/v1/tasks/{id}"]["delete"]["responses"]["204"]["description"]

    manifest = json.loads(run_manifest.read_text(encoding="utf-8"))
    assert manifest["status"] == "BLOCKED"
    assert manifest["blueprint"]["projectId"] == "sample-service"
    assert "frontend/src/generated/sample-service/GeneratedProjectPage.tsx" in manifest["generatedFiles"]
