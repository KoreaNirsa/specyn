from __future__ import annotations

import json
import os
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


def test_rewrite_npm_resolved_url_replaces_artifactory_prefix() -> None:
    url = (
        "https://packages.applied-caas-gateway1.internal.api.openai.org/"
        "artifactory/api/npm/npm-public/@tanstack/react-query/-/react-query-5.95.2.tgz"
    )

    rewritten = specyn_tasks.rewrite_npm_resolved_url(url)

    assert rewritten == "https://registry.npmjs.org/@tanstack/react-query/-/react-query-5.95.2.tgz"


def test_sanitize_npm_lockfile_rewrites_resolved_urls(tmp_path: Path) -> None:
    lockfile = tmp_path / "package-lock.json"
    lockfile.write_text(
        json.dumps(
            {
                "packages": {
                    "": {"name": "frontend"},
                    "node_modules/example": {
                        "resolved": (
                            "https://packages.applied-caas-gateway1.internal.api.openai.org/"
                            "artifactory/api/npm/npm-public/example/-/example-1.0.0.tgz"
                        )
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    rewritten_entries = specyn_tasks.sanitize_npm_lockfile(lockfile)
    rewritten = json.loads(lockfile.read_text(encoding="utf-8"))

    assert rewritten_entries == 1
    assert (
        rewritten["packages"]["node_modules/example"]["resolved"]
        == "https://registry.npmjs.org/example/-/example-1.0.0.tgz"
    )


def test_frontend_npm_install_command_uses_ci_when_lockfile_exists(monkeypatch, tmp_path: Path) -> None:
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / "package-lock.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(specyn_tasks, "FRONTEND_DIR", frontend_dir)

    command = specyn_tasks.frontend_npm_install_command()

    assert command[0:2] == ["npm", "ci"]
    assert "--include=optional" in command
    assert f"--registry={specyn_tasks.NPM_PUBLIC_REGISTRY.rstrip('/')}" in command


def test_clean_env_removes_proxy_related_variables(monkeypatch) -> None:
    monkeypatch.setenv("HTTP_PROXY", "http://proxy.example.com")
    monkeypatch.setenv("npm_config_registry", "https://mirror.example.com")
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", "/tmp/ca.pem")

    env = specyn_tasks.clean_env()

    assert "HTTP_PROXY" not in env
    assert "npm_config_registry" not in env
    assert "NODE_EXTRA_CA_CERTS" not in env
    assert env["NPM_CONFIG_REGISTRY"] == "https://registry.npmjs.org"


def test_run_checked_preserves_extra_env(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run(command, cwd, env):
        captured["command"] = command
        captured["cwd"] = cwd
        captured["env"] = env

        class Completed:
            returncode = 0

        return Completed()

    monkeypatch.setattr(specyn_tasks.subprocess, "run", fake_run)

    specyn_tasks.run_checked(["echo", "ok"], cwd=tmp_path, extra_env={"CUSTOM_FLAG": "1"})

    assert captured["command"] == ["echo", "ok"]
    assert captured["cwd"] == tmp_path
    assert captured["env"]["CUSTOM_FLAG"] == "1"


def test_backend_bootrun_command_uses_plain_quiet_no_daemon(monkeypatch, tmp_path: Path) -> None:
    local_gradle = tmp_path / "gradle.bat"
    local_gradle.write_text("@echo off\n", encoding="utf-8")

    monkeypatch.setattr(specyn_tasks, "local_gradle_executable", lambda: local_gradle)
    monkeypatch.setattr(specyn_tasks.shutil, "which", lambda binary: None)

    command = specyn_tasks.backend_bootrun_command()

    assert command == [
        str(local_gradle),
        "--console=plain",
        "--no-daemon",
        "--quiet",
        "bootRun",
    ]


class _RunningProcess:
    def poll(self):
        return None


class _StoppedProcess:
    def __init__(self, code: int) -> None:
        self.code = code

    def poll(self):
        return self.code


def test_wait_for_dev_services_prints_ready_message(monkeypatch, capsys) -> None:
    monkeypatch.setattr(specyn_tasks, "service_responding", lambda url: True)

    specyn_tasks.wait_for_dev_services(
        [
            ("AI Server", _RunningProcess()),
            ("Backend", _RunningProcess()),
            ("Frontend", _RunningProcess()),
        ]
    )

    output = capsys.readouterr().out
    assert "AI Server 준비 완료" in output
    assert "Backend 준비 완료" in output
    assert "Frontend 준비 완료" in output
    assert "모든 개발 서버 준비 완료" in output


def test_wait_for_dev_services_fails_when_a_process_exits(monkeypatch) -> None:
    monkeypatch.setattr(specyn_tasks, "service_responding", lambda url: False)

    try:
        specyn_tasks.wait_for_dev_services(
            [
                ("AI Server", _RunningProcess()),
                ("Backend", _StoppedProcess(1)),
                ("Frontend", _RunningProcess()),
            ]
        )
    except specyn_tasks.TaskError as exc:
        assert "Backend 프로세스가 비정상 종료되었습니다. exit=1" in str(exc)
    else:
        raise AssertionError("TaskError was not raised")


def test_task_sample_flow_runs_validate_compile_and_run(monkeypatch) -> None:
    calls: list[list[str]] = []

    monkeypatch.setattr(specyn_tasks, "task_validate_spec", lambda: calls.append(["validate"]))
    monkeypatch.setattr(specyn_tasks, "task_compile_prompts", lambda: calls.append(["compile-prompts"]))
    monkeypatch.setattr(specyn_tasks, "run_specyn", lambda command: calls.append(command))

    specyn_tasks.task_sample_flow()

    assert calls == [
        ["validate"],
        ["compile-prompts"],
        [
            "run",
            "--spec-dir",
            "specs/projects/sample-service",
            "--project-id",
            "sample-service",
            "--workspace",
            ".workspace/sample-service",
        ],
    ]
