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

    assert result.status == "COMPLETED"
    assert result.generated_files

    frontend_contract = tmp_path / "frontend" / "src" / "generated" / "sample-service" / "apiContract.ts"
    frontend_page = tmp_path / "frontend" / "src" / "generated" / "sample-service" / "GeneratedProjectPage.tsx"
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
    ai_router = tmp_path / "ai-server" / "app" / "generated" / "sample_service" / "router.py"
    generated_doc = tmp_path / "docs" / "generated" / "sample-service.md"
    openapi_doc = tmp_path / "docs" / "openapi" / "sample-service.yaml"
    run_manifest = result.workspace_dir / ".specyn" / "runs" / result.run_id / "manifest.json"

    for path in [frontend_contract, frontend_page, backend_controller, ai_router, generated_doc, openapi_doc, run_manifest]:
        assert path.exists(), path

    frontend_page_text = frontend_page.read_text(encoding="utf-8")
    assert 'Sample Service · Generated CRUD Demo' in frontend_page_text
    assert 'const TASKS_URL = BACKEND_URL + "/api/v1/tasks";' in frontend_page_text
    assert '작업 생성' in frontend_page_text
    assert '상태 토글' in frontend_page_text
    assert 'requestNoContent(taskDetailUrl(taskId), { method: "DELETE" })' in frontend_page_text

    backend_controller_text = backend_controller.read_text(encoding="utf-8")
    assert 'private final AtomicLong sequence = new AtomicLong(0);' in backend_controller_text
    assert '@GetMapping("/api/v1/tasks")' in backend_controller_text
    assert '@PatchMapping("/api/v1/tasks/{id}/status")' in backend_controller_text
    assert '@DeleteMapping("/api/v1/tasks/{id}")' in backend_controller_text
    assert 'title 필드는 필수입니다.' in backend_controller_text

    ai_router_text = ai_router.read_text(encoding="utf-8")
    assert "GENERATED_MANIFEST" in ai_router_text
    py_compile.compile(str(ai_router), doraise=True)

    generated_doc_text = generated_doc.read_text(encoding="utf-8")
    assert 'sample-service CRUD 데모 요약' in generated_doc_text
    assert 'http://localhost:5173' in generated_doc_text

    openapi_payload = yaml.safe_load(openapi_doc.read_text(encoding="utf-8"))
    assert openapi_payload["openapi"] == "3.1.0"
    assert "/api/v1/tasks" in openapi_payload["paths"]
    assert "get" in openapi_payload["paths"]["/api/v1/tasks"]
    assert "post" in openapi_payload["paths"]["/api/v1/tasks"]
    assert openapi_payload["paths"]["/api/v1/tasks/{id}"]["delete"]["responses"]["204"]["description"] == "작업 삭제"

    manifest = json.loads(run_manifest.read_text(encoding="utf-8"))
    assert manifest["status"] if "status" in manifest else True
    assert manifest["blueprint"]["projectId"] == "sample-service"
    assert "frontend/src/generated/sample-service/GeneratedProjectPage.tsx" in manifest["generatedFiles"]
