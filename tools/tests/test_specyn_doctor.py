"""
`specyn doctor` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from tools import specyn


def test_prepare_command_for_subprocess_wraps_windows_cmd(monkeypatch) -> None:
    """
    회귀 테스트로서 `prepare_command_for_subprocess_wraps_windows_cmd` 시나리오를 검증한다.

    주요 흐름은 `prepare_command_for_subprocess()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
    """
    monkeypatch.setattr(specyn, "is_windows", lambda: True)
    monkeypatch.setattr(
        specyn.shutil,
        "which",
        lambda binary: r"C:\\Program Files\\nodejs\\npm.cmd" if binary == "npm" else None,
    )

    prepared = specyn.prepare_command_for_subprocess(["npm", "-v"])

    assert prepared == ["cmd", "/c", r"C:\\Program Files\\nodejs\\npm.cmd", "-v"]


def test_repo_local_gradle_prefers_batch_launcher_on_windows(monkeypatch, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `repo_local_gradle_prefers_batch_launcher_on_windows` 시나리오를 검증한다.

    주요 흐름은 `repo_local_gradle()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    gradle_dir = tmp_path / "gradle-8.14" / "bin"
    gradle_dir.mkdir(parents=True)
    unix_launcher = gradle_dir / "gradle"
    batch_launcher = gradle_dir / "gradle.bat"
    unix_launcher.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    batch_launcher.write_text("@echo off\n", encoding="utf-8")

    monkeypatch.setattr(specyn, "LOCAL_GRADLE_DIR", tmp_path / "gradle-8.14")
    monkeypatch.setattr(specyn, "is_windows", lambda: True)

    resolved = specyn.repo_local_gradle()

    assert resolved == batch_launcher


def test_cmd_doctor_prefers_repo_local_gradle(monkeypatch, capsys, tmp_path: Path) -> None:
    """
    회귀 테스트로서 `cmd_doctor_prefers_repo_local_gradle` 시나리오를 검증한다.

    주요 흐름은 `chmod()`, `SimpleNamespace()`, `cmd_doctor()`, `Namespace()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.
        capsys: capsys과(와) 관련된 입력값이다.
        tmp_path: 파일 시스템 경로 객체다.
    """
    local_gradle = tmp_path / "gradle"
    local_gradle.write_text("#!/usr/bin/env bash\necho 'Gradle 8.14'\n", encoding="utf-8")
    local_gradle.chmod(0o755)

    monkeypatch.setattr(specyn, "repo_local_gradle", lambda: local_gradle)
    monkeypatch.setattr(specyn, "repo_venv_python", lambda: tmp_path / ".venv" / "bin" / "python")

    def fake_which(binary: str) -> str | None:
        """
        도구 모듈 테스트에서 `fake_which()`가 맡는 which 관련 작업을 수행한다.

        주요 흐름은 `get()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

        Args:
            binary: 문자열 입력값이다.

        Returns:
            함수에서 조립한 `str | None` 타입 결과다.
        """
        mapping = {
            "java": "/usr/bin/java",
            "node": "/usr/bin/node",
            "npm": "/usr/bin/npm",
        }
        return mapping.get(binary)

    monkeypatch.setattr(specyn.shutil, "which", fake_which)

    def fake_run(command, **kwargs):
        """
        도구 모듈 테스트에서 `fake_run()`가 맡는 run 관련 작업을 수행한다.

        주요 흐름은 `SimpleNamespace()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

        Args:
            command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.
            **kwargs: kwargs과(와) 관련된 입력값이다.

        Returns:
            이 함수가 계산하거나 조립한 결과 값이다.
        """
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


def test_command_report_marks_unexecutable_command_unavailable(monkeypatch) -> None:
    """
    회귀 테스트로서 `command_report_marks_unexecutable_command_unavailable` 시나리오를 검증한다.

    주요 흐름은 `OSError()`, `command_report()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        monkeypatch: monkeypatch과(와) 관련된 입력값이다.

    Raises:
        OSError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    monkeypatch.setattr(specyn, "is_windows", lambda: True)

    def fake_run(*args, **kwargs):
        """
        도구 모듈 테스트에서 `fake_run()`가 맡는 run 관련 작업을 수행한다.

        주요 흐름은 `OSError()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

        Args:
            *args: argparse가 전달한 서브커맨드 인자 네임스페이스다.
            **kwargs: kwargs과(와) 관련된 입력값이다.

        Raises:
            OSError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
        """
        raise OSError("[WinError 193] %1은(는) 올바른 Win32 응용 프로그램이 아닙니다")

    monkeypatch.setattr(specyn.subprocess, "run", fake_run)

    report = specyn.command_report([r"C:\\repo\\.specyn\\tools\\gradle-8.14\\bin\\gradle", "-v"])

    assert report["available"] is False
    assert report["version"].startswith("ERR: [WinError 193]")
    assert report["command"].endswith("gradle -v")
