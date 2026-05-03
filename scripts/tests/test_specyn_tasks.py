"""
`specyn tasks` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from scripts import specyn_tasks


def test_prepare_command_for_subprocess_wraps_windows_cmd(monkeypatch) -> None:
    """
    회귀 테스트로서 `prepare_command_for_subprocess_wraps_windows_cmd` 시나리오를 검증한다.

    주요 흐름은 `prepare_command_for_subprocess()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
    """
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
    """
    회귀 테스트로서 `prepare_command_for_subprocess_uses_bash_for_non_executable_script` 시나리오를 검증한다.

    주요 흐름은 `chmod()`, `prepare_command_for_subprocess()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
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
    """
    회귀 테스트로서 `resolve_gradle_command_prefers_repo_local_gradle` 시나리오를 검증한다.

    주요 흐름은 `resolve_gradle_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    local_gradle = tmp_path / "gradle.bat"
    local_gradle.write_text("@echo off\n", encoding="utf-8")

    monkeypatch.setattr(specyn_tasks, "local_gradle_executable", lambda: local_gradle)
    monkeypatch.setattr(specyn_tasks.shutil, "which", lambda binary: None)

    command = specyn_tasks.resolve_gradle_command()

    assert command == [str(local_gradle)]


def test_rewrite_npm_resolved_url_replaces_artifactory_prefix() -> None:
    """
    회귀 테스트로서 `rewrite_npm_resolved_url_replaces_artifactory_prefix` 시나리오를 검증한다.

    주요 흐름은 `rewrite_npm_resolved_url()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    url = (
        "https://packages.applied-caas-gateway1.internal.api.openai.org/"
        "artifactory/api/npm/npm-public/@tanstack/react-query/-/react-query-5.95.2.tgz"
    )

    rewritten = specyn_tasks.rewrite_npm_resolved_url(url)

    assert rewritten == "https://registry.npmjs.org/@tanstack/react-query/-/react-query-5.95.2.tgz"


def test_sanitize_npm_lockfile_rewrites_resolved_urls(tmp_path: Path) -> None:
    """
    회귀 테스트로서 `sanitize_npm_lockfile_rewrites_resolved_urls` 시나리오를 검증한다.

    주요 흐름은 `sanitize_npm_lockfile()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        tmp_path: 파일 시스템 경로 객체다.
    """
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
    """
    회귀 테스트로서 `frontend_npm_install_command_uses_ci_when_lockfile_exists` 시나리오를 검증한다.

    주요 흐름은 `frontend_npm_install_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / "package-lock.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(specyn_tasks, "FRONTEND_DIR", frontend_dir)

    command = specyn_tasks.frontend_npm_install_command()

    assert command[0:2] == ["npm", "ci"]
    assert "--include=optional" in command
    assert f"--registry={specyn_tasks.NPM_PUBLIC_REGISTRY.rstrip('/')}" in command


def test_clean_env_removes_proxy_related_variables(monkeypatch) -> None:
    """
    회귀 테스트로서 `clean_env_removes_proxy_related_variables` 시나리오를 검증한다.

    주요 흐름은 `setenv()`, `clean_env()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
    """
    monkeypatch.setenv("HTTP_PROXY", "http://proxy.example.com")
    monkeypatch.setenv("npm_config_registry", "https://mirror.example.com")
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", "/tmp/ca.pem")

    env = specyn_tasks.clean_env()

    assert "HTTP_PROXY" not in env
    assert "npm_config_registry" not in env
    assert "NODE_EXTRA_CA_CERTS" not in env
    assert env["NPM_CONFIG_REGISTRY"] == "https://registry.npmjs.org"


def test_run_checked_preserves_extra_env(monkeypatch, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `run_checked_preserves_extra_env` 시나리오를 검증한다.

    주요 흐름은 `Completed()`, `run_checked()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    captured: dict[str, object] = {}

    def fake_run(command, cwd, env):
        """
        스크립트 테스트에서 `fake_run()`가 맡는 run 관련 작업을 수행한다.

        주요 흐름은 `Completed()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

        Args:
            command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.
            cwd: 외부 명령을 실행할 현재 작업 디렉터리다.
            env: 환경 변수과(와) 관련된 입력값이다.

        Returns:
            이 함수가 계산하거나 조립한 결과 값이다.
        """
        captured["command"] = command
        captured["cwd"] = cwd
        captured["env"] = env

        class Completed:
            """
            스크립트 테스트에서 사용되는 `Completed` 클래스다.
            """
            returncode = 0

        return Completed()

    monkeypatch.setattr(specyn_tasks.subprocess, "run", fake_run)

    specyn_tasks.run_checked(["echo", "ok"], cwd=tmp_path, extra_env={"CUSTOM_FLAG": "1"})

    assert captured["command"] == ["echo", "ok"]
    assert captured["cwd"] == tmp_path
    assert captured["env"]["CUSTOM_FLAG"] == "1"


def test_backend_bootrun_command_uses_plain_quiet_no_daemon(monkeypatch, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `backend_bootrun_command_uses_plain_quiet_no_daemon` 시나리오를 검증한다.

    주요 흐름은 `backend_bootrun_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
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
    """
    스크립트 테스트에서 사용되는 `_RunningProcess` 클래스다.

    외부에서 주로 읽어야 할 메서드는 `poll()`이다.
    """
    def poll(self):
        """
        `_RunningProcess`의 공개 메서드로, `poll()`가 맡는 작업 관련 작업을 수행한다.

        외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.
        """
        return None


class _StoppedProcess:
    """
    스크립트 테스트에서 사용되는 `_StoppedProcess` 클래스다.

    외부에서 주로 읽어야 할 메서드는 `poll()`이다.

    Attributes:
        code: 종료 코드나 상태 코드 값이다.
    """
    def __init__(self, code: int) -> None:
        """
        `_StoppedProcess` 인스턴스가 사용할 기본 상태와 협력 객체를 준비한다.

        외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

        Args:
            code: 종료 코드나 상태 코드 값이다.
        """
        self.code = code

    def poll(self):
        """
        `_StoppedProcess`의 공개 메서드로, `poll()`가 맡는 작업 관련 작업을 수행한다.

        외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

        Returns:
            이 함수가 계산하거나 조립한 결과 값이다.
        """
        return self.code


def test_wait_for_dev_services_prints_ready_message(monkeypatch, capsys) -> None:
    """
    회귀 테스트로서 `wait_for_dev_services_prints_ready_message` 시나리오를 검증한다.

    주요 흐름은 `wait_for_dev_services()`, `_RunningProcess()`, `readouterr()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        capsys: capsys과(와) 관련된 입력값이다.
    """
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
    assert "대시보드 개발 서버 준비 완료" in output


def test_wait_for_dev_services_fails_when_a_process_exits(monkeypatch) -> None:
    """
    회귀 테스트로서 `wait_for_dev_services_fails_when_a_process_exits` 시나리오를 검증한다.

    주요 흐름은 `wait_for_dev_services()`, `_RunningProcess()`, `_StoppedProcess()`, `AssertionError()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.

    Raises:
        AssertionError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
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
    """
    회귀 테스트로서 `task_sample_flow_runs_validate_compile_and_run` 시나리오를 검증한다.

    주요 흐름은 `task_sample_flow()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
    """
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
            "specs/001-sample-service",
            "--project-id",
            "sample-service",
            "--workspace",
            ".workspace/sample-service",
        ],
    ]


def test_ensure_sample_runtime_generated_runs_specyn_when_runtime_missing(monkeypatch, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `ensure_sample_runtime_generated_runs_specyn_when_runtime_missing` 시나리오를 검증한다.

    주요 흐름은 `ensure_sample_runtime_generated()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    required = [
        tmp_path / "frontend" / "package.json",
        tmp_path / "backend" / "build.gradle.kts",
        tmp_path / "ai-server" / "app" / "main.py",
    ]
    calls: list[list[str]] = []

    def fake_run_specyn(command: list[str]) -> None:
        """
        스크립트 테스트에서 `fake_run_specyn()`가 맡는 run specyn 관련 작업을 수행한다.

        주요 흐름은 `append()`, `mkdir()`, `write_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Args:
            command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.
        """
        calls.append(command)
        for file_path in required:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("ok", encoding="utf-8")

    monkeypatch.setattr(specyn_tasks, "sample_runtime_required_files", lambda: required)
    monkeypatch.setattr(specyn_tasks, "run_specyn", fake_run_specyn)

    specyn_tasks.ensure_sample_runtime_generated()

    assert calls == [[
        "run",
        "--spec-dir",
        "specs/001-sample-service",
        "--project-id",
        "sample-service",
        "--workspace",
        ".workspace/sample-service",
    ]]


def test_ensure_frontend_dependencies_installs_when_node_modules_missing(monkeypatch, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `ensure_frontend_dependencies_installs_when_node_modules_missing` 시나리오를 검증한다.

    주요 흐름은 `ensure_frontend_dependencies()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    (frontend_dir / "package.json").write_text("{}", encoding="utf-8")
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(specyn_tasks, "sanitize_npm_lockfile", lambda path: calls.append(("sanitize", path)))
    monkeypatch.setattr(specyn_tasks, "run_checked", lambda command, cwd=None, extra_env=None: calls.append(("run", (command, cwd))))

    specyn_tasks.ensure_frontend_dependencies(frontend_dir, label="sample-service frontend")

    assert calls[0][0] == "sanitize" or calls[0][0] == "run"
    assert any(entry[0] == "run" for entry in calls)
