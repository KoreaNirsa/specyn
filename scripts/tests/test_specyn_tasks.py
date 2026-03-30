from __future__ import annotations

from pathlib import Path

from scripts import specyn_tasks


def test_prepare_command_for_subprocess_wraps_windows_cmd(monkeypatch) -> None:
    monkeypatch.setattr(specyn_tasks, "is_windows", lambda: True)
    monkeypatch.setattr(
        specyn_tasks.shutil,
        "which",
        lambda binary: r"C:\\Program Files\\nodejs\\npm.cmd" if binary == "npm" else None,
    )

    prepared = specyn_tasks.prepare_command_for_subprocess(["npm", "-v"])

    assert prepared == ["cmd", "/c", r"C:\\Program Files\\nodejs\\npm.cmd", "-v"]


def test_prepare_command_for_subprocess_uses_bash_for_non_executable_script(
    monkeypatch, tmp_path: Path
) -> None:
    wrapper = tmp_path / "gradlew"
    wrapper.write_text("#!/usr/bin/env bash\necho ok\n", encoding="utf-8")
    wrapper.chmod(0o644)

    monkeypatch.setattr(specyn_tasks, "is_windows", lambda: False)
    monkeypatch.setattr(
        specyn_tasks.shutil,
        "which",
        lambda binary: "/bin/bash" if binary == "bash" else None,
    )

    prepared = specyn_tasks.prepare_command_for_subprocess([str(wrapper), "bootRun"])

    assert prepared == ["bash", str(wrapper), "bootRun"]


def test_resolve_gradle_command_prefers_repo_local_gradle(monkeypatch, tmp_path: Path) -> None:
    local_gradle = tmp_path / "gradle.bat"
    local_gradle.write_text("@echo off\n", encoding="utf-8")

    monkeypatch.setattr(specyn_tasks, "local_gradle_executable", lambda: local_gradle)
    monkeypatch.setattr(specyn_tasks.shutil, "which", lambda binary: None)

    command = specyn_tasks.resolve_gradle_command()

    assert command == [str(local_gradle)]
