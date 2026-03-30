from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from tools import specyn


def test_prepare_command_for_subprocess_wraps_windows_cmd(monkeypatch) -> None:
    monkeypatch.setattr(specyn, "is_windows", lambda: True)
    monkeypatch.setattr(
        specyn.shutil,
        "which",
        lambda binary: r"C:\\Program Files\\nodejs\\npm.cmd" if binary == "npm" else None,
    )

    prepared = specyn.prepare_command_for_subprocess(["npm", "-v"])

    assert prepared == ["cmd", "/c", r"C:\\Program Files\\nodejs\\npm.cmd", "-v"]


def test_cmd_doctor_prefers_repo_local_gradle(monkeypatch, capsys, tmp_path: Path) -> None:
    local_gradle = tmp_path / "gradle"
    local_gradle.write_text("#!/usr/bin/env bash\necho 'Gradle 8.14'\n", encoding="utf-8")
    local_gradle.chmod(0o755)

    monkeypatch.setattr(specyn, "repo_local_gradle", lambda: local_gradle)
    monkeypatch.setattr(specyn, "repo_venv_python", lambda: tmp_path / ".venv" / "bin" / "python")

    def fake_which(binary: str) -> str | None:
        mapping = {
            "java": "/usr/bin/java",
            "node": "/usr/bin/node",
            "npm": "/usr/bin/npm",
        }
        return mapping.get(binary)

    monkeypatch.setattr(specyn.shutil, "which", fake_which)

    def fake_run(command, **kwargs):
        executable = command[0]
        if executable == str(local_gradle):
            return SimpleNamespace(stdout="Gradle 8.14\n")
        if executable == specyn.sys.executable:
            return SimpleNamespace(stdout="Python 3.12.0\n")
        if "java" in executable:
            return SimpleNamespace(stdout='openjdk version "21"\n')
        if "node" in executable:
            return SimpleNamespace(stdout="v20.0.0\n")
        if "npm" in executable:
            return SimpleNamespace(stdout="10.0.0\n")
        return SimpleNamespace(stdout="\n")

    monkeypatch.setattr(specyn.subprocess, "run", fake_run)

    exit_code = specyn.cmd_doctor(argparse.Namespace())
    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert exit_code == 0
    assert report["gradle"]["available"] is True
    assert report["gradle"]["source"] == "repo-local"
    assert report["gradle"]["version"] == "Gradle 8.14"
