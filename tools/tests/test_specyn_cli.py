from __future__ import annotations

import json
from pathlib import Path

from tools import local_sdd_runtime, prompt_compiler, specyn


def test_cmd_run_local_returns_generated_file_summary(monkeypatch, capsys, tmp_path: Path) -> None:
    monkeypatch.setattr(prompt_compiler, "AGENT_DIR", Path("agents"))
    monkeypatch.setattr(local_sdd_runtime, "PROMPT_ROOT_DIR", tmp_path / ".specyn" / "prompts")
    monkeypatch.setattr(local_sdd_runtime, "GENERATED_DOCS_DIR", tmp_path / "docs" / "generated")
    monkeypatch.setattr(local_sdd_runtime, "GENERATED_AI_SERVER_DIR", tmp_path / "ai-server" / "app" / "generated")
    monkeypatch.setattr(specyn, "ROOT_DIR", tmp_path)

    args = type("Args", (), {
        "spec_dir": "specs/projects/sample-service",
        "project_id": "sample-service",
        "workspace": ".workspace/sample-service",
        "backend_url": None,
        "rag_enabled": False,
        "runtime": "local",
    })()

    exit_code = specyn.cmd_run(args)
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["status"] == "COMPLETED"
    assert payload["projectId"] == "sample-service"
    assert payload["runtime"] == "local"
    assert "frontend/src/generated/sample-service/GeneratedProjectPage.tsx" in payload["generatedFiles"]
