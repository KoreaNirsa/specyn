"""
Specyn CLI의 실제 구현이 모여 있는 중심 모듈이다.
환경 파일 관리, Docker agent 점검, 인증 설정, spec 검증/프롬프트 컴파일/실행, 개발용 compose 제어까지 상위 명령 흐름 대부분을 이 파일이 조율한다.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from typing import Any
import urllib.error
import urllib.request

ROOT_DIR = Path(__file__).resolve().parents[1]
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(ROOT_DIR))

TEMPLATE_DIR = ROOT_DIR / "specs" / "templates"
PROMPT_ROOT_DIR = Path(".specyn") / "prompts"
ENV_FILE = ROOT_DIR / ".env"
ENV_EXAMPLE_FILE = ROOT_DIR / ".env.example"
CODEX_HOME_DIR = ROOT_DIR / ".specyn" / "codex"
CODEX_AUTH_FILE = CODEX_HOME_DIR / "auth.json"
DASHBOARD_COMPOSE_FILE = ROOT_DIR / "docker-compose.local.yml"
SAMPLE_COMPOSE_FILE = ROOT_DIR / "projects" / "sample-service" / "docker-compose.local.yml"
DASHBOARD_AGENT_SERVICE = "dashboard-ai-server"
DEFAULT_SETUP_MODEL = "gpt-5.4"
DEFAULT_SETUP_AUTH_MODE = "chatgpt"
VENV_REEXEC_ENV = "SPECYN_RUNNING_FROM_REPO_VENV"
LOCAL_GRADLE_VERSION = os.environ.get("SPECYN_GRADLE_VERSION", "8.14")
LOCAL_GRADLE_DIR = ROOT_DIR / ".specyn" / "tools" / f"gradle-{LOCAL_GRADLE_VERSION}"
WINDOWS_SHELL_EXTENSIONS = {".cmd", ".bat"}
DOCKER_VERIFY_SENTINEL = "specyn-codex-verified"


def safe_print(message: str) -> None:
    """Print with a replacement fallback for non-UTF-8 consoles."""
    try:
        print(message)
        return
    except UnicodeEncodeError:
        pass

    stream = sys.stdout
    encoding = getattr(stream, "encoding", None) or "utf-8"
    fallback = message.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(fallback)
CODEX_OAUTH_CALLBACK_PORT = 1455


def is_windows() -> bool:
    """
    도구 계층에서 windows 여부를 판단한다.

    외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    return os.name == "nt"


def format_command(command: list[str]) -> str:
    """
    도구 계층에서 command을(를) 실행/표시용 문자열로 정리한다.

    주요 흐름은 `is_windows()`, `list2cmdline()`, `quote()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    if is_windows():
        return subprocess.list2cmdline(command)
    return " ".join(shlex.quote(part) for part in command)


def repo_venv_python() -> Path | None:
    """
    도구 계층에서 `repo_venv_python()`가 맡는 가상환경 Python 관련 작업을 수행한다.

    주요 흐름은 `exists()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    candidates = [
        ROOT_DIR / ".venv" / "bin" / "python",
        ROOT_DIR / ".venv" / "Scripts" / "python.exe",
        ROOT_DIR / ".venv" / "Scripts" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def repo_local_gradle() -> Path | None:
    """
    도구 계층에서 `repo_local_gradle()`가 맡는 로컬 Gradle 관련 작업을 수행한다.

    주요 흐름은 `is_windows()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    if is_windows():
        candidates = [
            LOCAL_GRADLE_DIR / "bin" / "gradle.bat",
            LOCAL_GRADLE_DIR / "bin" / "gradle",
        ]
    else:
        candidates = [
            LOCAL_GRADLE_DIR / "bin" / "gradle",
            LOCAL_GRADLE_DIR / "bin" / "gradle.bat",
        ]

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def normalize_path(value: str | Path) -> str:
    """
    도구 계층에서 경로을(를) 일관된 표준 형태로 정규화한다.

    주요 흐름은 `str()`, `Path()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        value: 정규화하거나 판정할 단일 값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return str(Path(value))


def should_reexec_into_repo_venv(command: str | None) -> bool:
    """
    도구 계층에서 reexec into repo 가상환경 여부를 판단한다.

    주요 흐름은 `repo_venv_python()`, `samefile()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        command: 판단하거나 실행할 서브커맨드 이름 또는 명령 문자열이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    if command in {None, "doctor", "setup", "up", "sample-up", "down", "sample-down", "auth-status"}:
        return False

    venv_python = repo_venv_python()
    if venv_python is None:
        return False

    current_python = Path(sys.executable).resolve()
    try:
        if current_python.samefile(venv_python):
            return False
    except FileNotFoundError:
        pass

    return os.environ.get(VENV_REEXEC_ENV) != "1"


def reexec_into_repo_venv() -> None:
    """
    도구 계층에서 `reexec_into_repo_venv()`가 맡는 into repo 가상환경 관련 작업을 수행한다.

    주요 흐름은 `repo_venv_python()`, `SystemExit()`, `call()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Raises:
        SystemExit: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    venv_python = repo_venv_python()
    if venv_python is None:
        return

    env = os.environ.copy()
    env[VENV_REEXEC_ENV] = "1"
    command = [str(venv_python), str(ROOT_DIR / "specyn.py"), *sys.argv[1:]]
    raise SystemExit(subprocess.call(command, cwd=str(ROOT_DIR), env=env))


def load_prompt_tooling() -> tuple[Any, Any, Any, Any, Any] | None:
    """
    도구 계층에서 프롬프트 tooling을(를) 외부 소스에서 읽어 들인다.

    주요 흐름은 `print()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        함수에서 조립한 `tuple[Any, Any, Any, Any, Any] | None` 타입 결과다.
    """
    try:
        from tools.agent_flow import build_execution_plan, resolve_agent_flow
        from tools.prompt_compiler import compile_prompt
        from tools.spec_loader import load_spec_bundle
        from tools.validators import validate_bundle
    except ModuleNotFoundError as error:
        print(f"TOOLING_IMPORT_FAILED: {error}")
        return None

    return compile_prompt, load_spec_bundle, validate_bundle, resolve_agent_flow, build_execution_plan


def load_runtime_tooling() -> Any | None:
    """
    도구 계층에서 런타임 tooling을(를) 외부 소스에서 읽어 들인다.

    주요 흐름은 `print()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        함수에서 조립한 `Any | None` 타입 결과다.
    """
    try:
        from tools.local_sdd_runtime import LocalSddRuntime
    except ModuleNotFoundError as error:
        print(f"TOOLING_IMPORT_FAILED: {error}")
        return None
    return LocalSddRuntime


def load_bundle_or_report(load_spec_bundle: Any, spec_dir: str) -> dict[str, Any] | None:
    """
    도구 계층에서 spec 번들 or 리포트을(를) 외부 소스에서 읽어 들인다.

    주요 흐름은 `load_spec_bundle()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        load_spec_bundle: load spec spec 번들을(를) 나타내는 `Any` 타입 입력값이다.
        spec_dir: spec 문서가 위치한 디렉터리다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    try:
        return load_spec_bundle(Path(spec_dir))
    except (FileNotFoundError, ValueError) as error:
        print(f"SPEC_LOAD_FAILED: {error}")
        return None


def bundle_to_request(project_id: str, bundle: dict[str, Any], workspace: str, rag_enabled: bool) -> dict[str, Any]:
    """
    도구 계층에서 `bundle_to_request()`가 맡는 to 요청 관련 작업을 수행한다.

    주요 흐름은 `values()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.
        bundle: spec type을 키로 갖는 spec 문서 번들이다.
        workspace: 작업 또는 생성 대상 워크스페이스 경로다.
        rag_enabled: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    documents = [
        {"name": document.name, "type": document.spec_type, "content": document.raw_content}
        for document in bundle.values()
    ]
    return {
        "projectId": project_id,
        "documents": documents,
        "ragEnabled": rag_enabled,
        "dryRun": False,
        "workspacePath": workspace,
    }


def prepare_command_for_subprocess(command: list[str]) -> list[str]:
    """
    도구 계층에서 `prepare_command_for_subprocess()`가 맡는 command for 하위 프로세스 관련 작업을 수행한다.

    주요 흐름은 `ValueError()`, `is_windows()`, `which()`, `is_file()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.

    Raises:
        ValueError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    if not command:
        raise ValueError("command must not be empty")

    prepared = list(command)
    executable = prepared[0]

    if is_windows():
        if not any(separator in executable for separator in (os.sep, "/", "\\")):
            resolved = shutil.which(executable)
            if resolved:
                executable = resolved
        prepared[0] = executable
        if Path(executable).suffix.lower() in WINDOWS_SHELL_EXTENSIONS:
            return ["cmd", "/c", executable, *prepared[1:]]
        return prepared

    path = Path(executable)
    if path.exists() and path.is_file() and not os.access(path, os.X_OK):
        if shutil.which("bash"):
            return ["bash", str(path), *prepared[1:]]
    return prepared


def command_report(command: list[str], *, source: str | None = None) -> dict[str, Any]:
    """
    도구 계층에서 `command_report()`가 맡는 리포트 관련 작업을 수행한다.

    주요 흐름은 `prepare_command_for_subprocess()`, `run()`, `splitlines()`, `format_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.
        source: 비교 또는 복사 기준이 되는 입력 소스다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    prepared = prepare_command_for_subprocess(command)
    item: dict[str, Any] = {"available": True}
    if source is not None:
        item["source"] = source

    try:
        completed = subprocess.run(
            prepared,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            text=True,
        )
        first_line = (completed.stdout or "").splitlines()[0] if completed.stdout else ""
        item["version"] = first_line
    except Exception as error:  # pragma: no cover
        item["available"] = False
        item["version"] = f"ERR: {error}"
        item["command"] = format_command(prepared)

    return item


def resolve_project_id(project_id: str | None, spec_dir: str) -> str:
    """
    도구 계층에서 프로젝트 id의 최종 값을 결정한다.

    주요 흐름은 `strip()`, `Path()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.
        spec_dir: spec 문서가 위치한 디렉터리다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return project_id.strip() if project_id and project_id.strip() else Path(spec_dir).name


def resolve_workspace_path(workspace: str | None, project_id: str) -> str:
    """
    도구 계층에서 워크스페이스 경로의 최종 값을 결정한다.

    주요 흐름은 `normalize_path()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        workspace: 작업 또는 생성 대상 워크스페이스 경로다.
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return normalize_path(workspace) if workspace and workspace.strip() else normalize_path(Path(".workspace") / project_id)


def resolve_project_output_root(project_id: str) -> Path:
    """
    도구 계층에서 프로젝트 출력 root의 최종 값을 결정한다.

    외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

    Args:
        project_id: 생성 또는 실행 대상 프로젝트 식별자다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    return ROOT_DIR / "projects" / project_id


def display_path(path: Path) -> str:
    """
    도구 계층에서 경로을(를) 표시하기 쉬운 형태로 바꾼다.

    주요 흐름은 `str()`, `relative_to()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        path: 처리 대상 경로다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    try:
        return str(path.relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def print_validation_issues(issues: list[Any]) -> None:
    """
    도구 계층에서 검증 이슈 목록을(를) 사용자에게 출력한다.

    주요 흐름은 `print()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        issues: 순서를 유지하는 목록 입력값이다.
    """
    for issue in issues:
        safe_print(f"[{issue.level}] {issue.code}: {issue.message}")


def ensure_env_file() -> Path:
    """
    도구 계층에서 환경 변수 파일이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `copy2()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    if not ENV_FILE.exists():
        shutil.copy2(ENV_EXAMPLE_FILE, ENV_FILE)
    return ENV_FILE


def load_env_values(path: Path = ENV_FILE) -> dict[str, str]:
    """
    도구 계층에서 환경 변수 값 목록을(를) 외부 소스에서 읽어 들인다.

    주요 흐름은 `splitlines()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        path: 처리 대상 경로다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or "=" not in raw_line:
            continue
        key, _, value = raw_line.partition("=")
        values[key.strip()] = value.strip()
    return values


def write_env_updates(updates: dict[str, str], path: Path = ENV_FILE) -> None:
    """
    도구 계층에서 환경 변수 updates을(를) 파일이나 설정으로 기록한다.

    주요 흐름은 `ensure_env_file()`, `splitlines()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        updates: 키-값 형태의 매핑 입력값이다.
        path: 처리 대상 경로다.
    """
    ensure_env_file()
    lines = path.read_text(encoding="utf-8").splitlines()
    written_keys: set[str] = set()
    rendered: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            rendered.append(line)
            continue
        key, _, _ = line.partition("=")
        normalized_key = key.strip()
        if normalized_key in updates:
            rendered.append(f"{normalized_key}={updates[normalized_key]}")
            written_keys.add(normalized_key)
            continue
        rendered.append(line)

    missing_items = [(key, value) for key, value in updates.items() if key not in written_keys]
    if missing_items and rendered and rendered[-1] != "":
        rendered.append("")
    for key, value in missing_items:
        rendered.append(f"{key}={value}")

    path.write_text("\n".join(rendered).rstrip() + "\n", encoding="utf-8")


def mask_secret(value: str | None) -> str:
    """
    도구 계층에서 비밀값을(를) 노출되지 않게 가린다.

    주요 흐름은 `len()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        value: 정규화하거나 판정할 단일 값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    if not value:
        return "<empty>"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def completed_output(completed: subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]) -> str:
    """
    도구 계층에서 `completed_output()`가 맡는 출력 관련 작업을 수행한다.

    주요 흐름은 `isinstance()`, `decode()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        completed: completed을(를) 나타내는 `subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]` 타입 입력값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    output = completed.stdout
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace").strip()
    return (output or "").strip()


def docker_cli_available() -> bool:
    """
    도구 계층에서 `docker_cli_available()`가 맡는 CLI available 관련 작업을 수행한다.

    주요 흐름은 `which()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    return shutil.which("docker") is not None


def docker_daemon_status() -> tuple[bool, str]:
    """
    도구 계층에서 `docker_daemon_status()`가 맡는 데몬 상태 관련 작업을 수행한다.

    주요 흐름은 `docker_cli_available()`, `run_command()`, `docker_command()`, `completed_output()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    if not docker_cli_available():
        return False, "docker-not-installed"

    try:
        completed = run_command(
            [*docker_command("info", "--format", "{{.ServerVersion}}")],
            cwd=ROOT_DIR,
            capture_output=True,
        )
    except FileNotFoundError:
        return False, "docker-cli-not-executable"

    output = completed_output(completed)
    if completed.returncode != 0:
        return False, output or "docker-daemon-unavailable"
    return True, output.splitlines()[0] if output else "docker-daemon-ready"


def codex_cached_login_hint() -> tuple[bool, str]:
    """
    도구 계층에서 `codex_cached_login_hint()`가 맡는 캐시된 상태 로그인 hint 관련 작업을 수행한다.

    주요 흐름은 `display_path()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    if not CODEX_AUTH_FILE.exists():
        return False, "auth-cache-missing"
    try:
        payload = json.loads(CODEX_AUTH_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return True, f"auth-cache-present:{display_path(CODEX_AUTH_FILE)}"

    provider = payload.get("provider") or payload.get("type") or payload.get("auth_type") or "unknown"
    return True, f"auth-cache-present:{provider}"


def summarize_docker_agent_state() -> dict[str, Any]:
    """
    도구 계층에서 Docker agent 상태을(를) 요약한다.

    주요 흐름은 `docker_cli_available()`, `docker_daemon_status()`, `codex_cached_login_hint()`, `ensure_codex_in_agent()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    docker_cli = docker_cli_available()
    docker_ready, docker_detail = docker_daemon_status() if docker_cli else (False, "docker-not-installed")
    cached_logged_in, cached_login_detail = codex_cached_login_hint()

    summary: dict[str, Any] = {
        "dockerCliAvailable": docker_cli,
        "dockerDaemonReady": docker_ready,
        "dockerDaemonStatus": docker_detail,
        "codexLoginCached": cached_logged_in,
        "codexLoginStatus": cached_login_detail,
        "codexInstalledInDocker": False,
        "codexVersion": "not-checked",
    }

    if not docker_ready or not DASHBOARD_COMPOSE_FILE.exists():
        if not DASHBOARD_COMPOSE_FILE.exists():
            summary["codexInstalledInDocker"] = False
            summary["codexVersion"] = "compose-file-missing"
        return summary

    codex_available, codex_detail = ensure_codex_in_agent(install_if_missing=False)
    summary["codexInstalledInDocker"] = codex_available
    summary["codexVersion"] = codex_detail
    if not codex_available:
        summary["codexLoginStatus"] = codex_detail
        return summary

    logged_in, login_detail = codex_login_status()
    summary["codexLoginCached"] = logged_in
    summary["codexLoginStatus"] = login_detail
    return summary


def ensure_docker_ready_for_command(command_name: str) -> tuple[bool, str]:
    """
    도구 계층에서 Docker ready for command이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `docker_cli_available()`, `docker_daemon_status()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        command_name: 문자열 입력값이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    if not docker_cli_available():
        detail = "docker 명령을 찾을 수 없습니다. Docker Desktop 또는 Docker Engine + Compose v2가 필요합니다."
        print(f"{command_name}_FAILED: {detail}")
        return False, detail

    ready, detail = docker_daemon_status()
    if ready:
        return True, detail

    print(
        f"{command_name}_FAILED: Docker Desktop/daemon 이 실행 중이 아니거나 연결할 수 없습니다. detail={detail}"
    )
    return False, detail


def ensure_codex_home() -> None:
    """
    도구 계층에서 Codex 홈 디렉터리이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `mkdir()`, `exists()`, `read_text()`, `write_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    CODEX_HOME_DIR.mkdir(parents=True, exist_ok=True)
    config_path = CODEX_HOME_DIR / "config.toml"
    if config_path.exists() and "cli_auth_credentials_store" in config_path.read_text(encoding="utf-8"):
        return
    config_path.write_text(
        "# Managed by Specyn CLI\ncli_auth_credentials_store = \"file\"\n",
        encoding="utf-8",
    )


def docker_command(*parts: str | Path) -> list[str]:
    """
    도구 계층에서 `docker_command()`가 맡는 command 관련 작업을 수행한다.

    주요 흐름은 `normalize_path()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        *parts: parts을(를) 나타내는 `str | Path` 타입 입력값이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    return ["docker", *(normalize_path(part) for part in parts)]


def run_command(
    command: list[str],
    *,
    cwd: Path = ROOT_DIR,
    capture_output: bool = False,
    text: bool = True,
    input_text: str | None = None,
    env: dict[str, str] | None = None,
    check: bool = False,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    """
    도구 계층에서 command을(를) 실제로 실행한다.

    주요 흐름은 `prepare_command_for_subprocess()`, `run()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.
        cwd: 외부 명령을 실행할 현재 작업 디렉터리다.
        capture_output: 기능 사용 여부를 나타내는 불리언 값이다.
        text: 파싱, 정규화, 검색 대상이 되는 문자열이다.
        input_text: input 텍스트을(를) 나타내는 `str | None` 타입 입력값이다.
        env: 키-값 형태의 매핑 입력값이다.
        check: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        외부 명령 실행 결과를 담은 `subprocess.CompletedProcess` 객체다.
    """
    prepared = prepare_command_for_subprocess(command)
    return subprocess.run(
        prepared,
        cwd=cwd,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.STDOUT if capture_output else None,
        text=text,
        input=input_text,
        env=env,
        check=check,
    )


def compose_run_agent_command(
    agent_command: list[str],
    *,
    capture_output: bool = False,
    input_text: str | None = None,
    published_ports: list[str] | None = None,
    check: bool = False,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    """
    도구 계층에서 run agent command을(를) 여러 입력으로 합성한다.

    주요 흐름은 `ensure_codex_home()`, `docker_command()`, `run_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        agent_command: 순서를 유지하는 목록 입력값이다.
        capture_output: 기능 사용 여부를 나타내는 불리언 값이다.
        input_text: input 텍스트을(를) 나타내는 `str | None` 타입 입력값이다.
        published_ports: 순서를 유지하는 목록 입력값이다.
        check: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        외부 명령 실행 결과를 담은 `subprocess.CompletedProcess` 객체다.
    """
    ensure_codex_home()
    port_flags: list[str] = []
    for published_port in published_ports or []:
        port_flags.extend(["-p", published_port])
    command = [
        *docker_command("compose", "-f", DASHBOARD_COMPOSE_FILE),
        "run",
        "--rm",
        "--no-deps",
        *port_flags,
        DASHBOARD_AGENT_SERVICE,
        *agent_command,
    ]
    return run_command(
        command,
        cwd=ROOT_DIR,
        capture_output=capture_output,
        input_text=input_text,
        check=check,
    )


def build_dashboard_agent_image() -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    """
    도구 계층에서 dashboard agent image을(를) 조립하거나 생성한다.

    주요 흐름은 `run_command()`, `docker_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        외부 명령 실행 결과를 담은 `subprocess.CompletedProcess` 객체다.
    """
    return run_command(
        [*docker_command("compose", "-f", DASHBOARD_COMPOSE_FILE), "build", DASHBOARD_AGENT_SERVICE],
        cwd=ROOT_DIR,
    )


def verify_codex_in_agent() -> tuple[bool, str]:
    """
    도구 계층에서 `verify_codex_in_agent()`가 맡는 Codex in agent 관련 작업을 수행한다.

    주요 흐름은 `compose_run_agent_command()`, `completed_output()`, `splitlines()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    completed = compose_run_agent_command(
        ["bash", "-lc", f"codex --version && printf '\n{DOCKER_VERIFY_SENTINEL}\n'"],
        capture_output=True,
    )
    output = completed_output(completed)
    if completed.returncode != 0:
        return False, output
    if DOCKER_VERIFY_SENTINEL not in output:
        return False, output
    version_line = output.splitlines()[0] if output else ""
    return True, version_line


def ensure_codex_in_agent(*, install_if_missing: bool) -> tuple[bool, str]:
    """
    도구 계층에서 Codex in agent이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `verify_codex_in_agent()`, `build_dashboard_agent_image()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        install_if_missing: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    available, detail = verify_codex_in_agent()
    if available or not install_if_missing:
        return available, detail
    build_dashboard_agent_image()
    return verify_codex_in_agent()


def codex_login_status() -> tuple[bool, str]:
    """
    도구 계층에서 `codex_login_status()`가 맡는 로그인 상태 관련 작업을 수행한다.

    주요 흐름은 `compose_run_agent_command()`, `completed_output()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    completed = compose_run_agent_command(["codex", "login", "status"], capture_output=True)
    output = completed_output(completed)
    return completed.returncode == 0, output


def codex_logout() -> int:
    """
    도구 계층에서 `codex_logout()`가 맡는 로그아웃 관련 작업을 수행한다.

    주요 흐름은 `compose_run_agent_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    completed = compose_run_agent_command(["codex", "logout"])
    return completed.returncode


def codex_login_with_api_key(api_key: str) -> int:
    """
    도구 계층에서 `codex_login_with_api_key()`가 맡는 로그인 with API key 관련 작업을 수행한다.

    주요 흐름은 `compose_run_agent_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        api_key: 문자열 입력값이다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    completed = compose_run_agent_command(["codex", "login", "--with-api-key"], input_text=api_key)
    return completed.returncode


def host_codex_login_command() -> list[str] | None:
    """
    도구 계층에서 `host_codex_login_command()`가 맡는 Codex 로그인 command 관련 작업을 수행한다.

    주요 흐름은 `which()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    if shutil.which("codex") is not None:
        return ["codex", "login"]
    if shutil.which("npx") is not None:
        return ["npx", "@openai/codex@latest", "login"]
    return None


def codex_login_with_chatgpt(*, device_auth: bool) -> int:
    """
    도구 계층에서 `codex_login_with_chatgpt()`가 맡는 로그인 with ChatGPT 관련 작업을 수행한다.

    주요 흐름은 `host_codex_login_command()`, `run_command()`, `compose_run_agent_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        device_auth: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    if not device_auth:
        command = host_codex_login_command()
        if command is None:
            print("SETUP_FAILED: Host Codex CLI를 찾지 못했습니다. `codex` 또는 `npx`가 필요합니다.")
            return 1
        env = os.environ.copy()
        env["CODEX_HOME"] = str(CODEX_HOME_DIR)
        completed = run_command(command, cwd=ROOT_DIR, env=env)
        return completed.returncode

    command = ["codex", "login"]
    command.append("--device-auth")
    published_ports = None
    completed = compose_run_agent_command(command, published_ports=published_ports)
    return completed.returncode


def prompt_choice(message: str, options: list[tuple[str, str]], *, default: str | None = None) -> str:
    """
    도구 계층에서 choice에 대해 사용자 입력을 받는다.

    주요 흐름은 `input()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        message: 출력하거나 전달할 메시지 문자열이다.
        options: 순서를 유지하는 목록 입력값이다.
        default: 원시 값을 해석할 수 없을 때 사용할 기본값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    indexed = {str(index): key for index, (key, _) in enumerate(options, start=1)}
    by_key = {key: key for key, _ in options}
    rendered = ", ".join(f"{index}. {label}" for index, (_, label) in enumerate(options, start=1))
    default_suffix = f" [default: {default}]" if default else ""
    while True:
        raw = input(f"{message}\n{rendered}{default_suffix}\n> ").strip()
        if not raw and default is not None:
            return default
        if raw in indexed:
            return indexed[raw]
        if raw in by_key:
            return by_key[raw]
        print("유효한 번호 또는 키를 입력하세요.")


def prompt_text(message: str, *, default: str | None = None, secret: bool = False) -> str:
    """
    도구 계층에서 텍스트에 대해 사용자 입력을 받는다.

    주요 흐름은 `getpass()`, `input()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        message: 출력하거나 전달할 메시지 문자열이다.
        default: 원시 값을 해석할 수 없을 때 사용할 기본값이다.
        secret: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    suffix = f" [default: {default}]" if default else ""
    while True:
        if secret:
            raw = getpass.getpass(f"{message}{suffix}\n> ")
        else:
            raw = input(f"{message}{suffix}\n> ")
        value = raw.strip()
        if value:
            return value
        if default is not None:
            return default
        print("값을 비워 둘 수 없습니다.")


def select_model(current_model: str | None, provided_model: str | None) -> str:
    """
    도구 계층에서 모델을(를) 선택한다.

    주요 흐름은 `prompt_choice()`, `prompt_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        current_model: current 모델을(를) 나타내는 `str | None` 타입 입력값이다.
        provided_model: provided 모델을(를) 나타내는 `str | None` 타입 입력값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    if provided_model:
        return provided_model.strip()
    default_model = current_model or DEFAULT_SETUP_MODEL
    options: list[tuple[str, str]] = []
    seen: set[str] = set()
    for candidate in [default_model, "gpt-5.4", "gpt-5.3-codex", "custom"]:
        if candidate in seen:
            continue
        seen.add(candidate)
        label = candidate if candidate != "custom" else "직접 입력"
        options.append((candidate, label))
    selected = prompt_choice("사용할 모델을 선택하세요.", options, default=default_model)
    if selected == "custom":
        return prompt_text("사용할 모델명을 입력하세요.", default=default_model)
    return selected


def resolve_openapi_key(
    existing_key: str | None,
    *,
    provided_api_key: str | None,
    non_interactive: bool,
) -> str:
    """
    도구 계층에서 OpenAI API key의 최종 값을 결정한다.

    주요 흐름은 `prompt_text()`, `prompt_choice()`, `mask_secret()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        existing_key: existing key을(를) 나타내는 `str | None` 타입 입력값이다.
        provided_api_key: provided API key을(를) 나타내는 `str | None` 타입 입력값이다.
        non_interactive: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    if provided_api_key is not None:
        return provided_api_key.strip()
    if non_interactive:
        return (existing_key or "").strip()

    if not existing_key:
        return prompt_text("OPENAI API Key를 입력하세요.", secret=True)

    action = prompt_choice(
        f"기존 OPENAI API Key가 있습니다. ({mask_secret(existing_key)})",
        [
            ("keep", "유지"),
            ("modify", "수정"),
            ("remove", "제거"),
        ],
        default="keep",
    )
    if action == "modify":
        return prompt_text("새 OPENAI API Key를 입력하세요.", secret=True)
    if action == "remove":
        return ""
    return existing_key


def resolve_chatgpt_action(
    *,
    logged_in: bool,
    provided_action: str | None,
    non_interactive: bool,
) -> str:
    """
    도구 계층에서 ChatGPT action의 최종 값을 결정한다.

    주요 흐름은 `prompt_choice()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        logged_in: 기능 사용 여부를 나타내는 불리언 값이다.
        provided_action: provided action을(를) 나타내는 `str | None` 타입 입력값이다.
        non_interactive: 기능 사용 여부를 나타내는 불리언 값이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    if provided_action:
        return provided_action
    if non_interactive:
        return "reuse" if logged_in else "relogin"
    if logged_in:
        return prompt_choice(
            "이미 인증된 ChatGPT 계정이 있습니다. 어떻게 진행할까요?",
            [
                ("reuse", "현재 인증 유지"),
                ("relogin", "로그아웃 후 다시 로그인"),
                ("logout", "로그아웃만 수행"),
            ],
            default="reuse",
        )
    return "relogin"


def env_summary() -> dict[str, Any]:
    """
    도구 계층에서 `env_summary()`가 맡는 요약 관련 작업을 수행한다.

    주요 흐름은 `load_env_values()`, `display_path()`, `mask_secret()`, `summarize_docker_agent_state()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    values = load_env_values(ENV_FILE)
    summary = {
        "envFile": display_path(ENV_FILE),
        "authMode": values.get("SPECYN_AUTH_MODE", DEFAULT_SETUP_AUTH_MODE),
        "apiKeyConfigured": bool(values.get("OPENAI_API_KEY", "").strip()),
        "apiKeyMasked": mask_secret(values.get("OPENAI_API_KEY", "")),
        "openaiModel": values.get("OPENAI_MODEL", DEFAULT_SETUP_MODEL),
        "codexModel": values.get("CODEX_MODEL", DEFAULT_SETUP_MODEL),
        "codexHome": display_path(CODEX_HOME_DIR),
    }
    summary.update(summarize_docker_agent_state())
    return summary


def cmd_validate(args: argparse.Namespace) -> int:
    """
    `validate` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `load_prompt_tooling()`, `load_bundle_or_report()`, `validate_bundle()`, `print_validation_issues()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        args: argparse가 전달한 서브커맨드 인자 네임스페이스다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    tooling = load_prompt_tooling()
    if tooling is None:
        return 1
    _, load_spec_bundle, validate_bundle, _, _ = tooling
    bundle = load_bundle_or_report(load_spec_bundle, args.spec_dir)
    if bundle is None:
        return 1
    issues = validate_bundle(bundle)
    if not issues:
        print("VALIDATION_OK")
        return 0
    print_validation_issues(issues)
    return 1


def cmd_init_spec(args: argparse.Namespace) -> int:
    """
    `init_spec` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `glob()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        args: argparse가 전달한 서브커맨드 인자 네임스페이스다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for template_path in sorted(TEMPLATE_DIR.glob("*.md")):
        content = template_path.read_text(encoding="utf-8").replace("{{project_id}}", args.project_id)
        target = output_dir / template_path.name
        if target.exists() and not args.overwrite:
            print(f"SKIP {target}")
            continue
        target.write_text(content, encoding="utf-8")
        print(f"CREATED {target}")
    return 0


def cmd_compile_prompts(args: argparse.Namespace) -> int:
    """
    `compile_prompts` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `load_prompt_tooling()`, `load_bundle_or_report()`, `validate_bundle()`, `print_validation_issues()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        args: argparse가 전달한 서브커맨드 인자 네임스페이스다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    tooling = load_prompt_tooling()
    if tooling is None:
        return 1
    compile_prompt, load_spec_bundle, validate_bundle, resolve_agent_flow, build_execution_plan = tooling
    bundle = load_bundle_or_report(load_spec_bundle, args.spec_dir)
    if bundle is None:
        return 1
    issues = validate_bundle(bundle)
    if issues:
        print_validation_issues(issues)
        return 1

    project_id = resolve_project_id(getattr(args, "project_id", None), args.spec_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    previous_outputs: list[str] = []
    workspace_path = resolve_workspace_path(args.workspace, project_id)
    base_flow = resolve_agent_flow(bundle, rag_enabled=getattr(args, "rag_enabled", False)).execution_flow
    execution_plan = build_execution_plan(bundle, rag_enabled=getattr(args, "rag_enabled", False))
    print(f"AGENT_FLOW {' -> '.join(base_flow)}")
    if any(step.phase != "main" for step in execution_plan):
        print("EXECUTION_PLAN " + " -> ".join(step.label for step in execution_plan))
    for step in execution_plan:
        prompt = compile_prompt(
            agent_name=step.agent,
            bundle=bundle,
            previous_outputs=previous_outputs,
            workspace_path=workspace_path,
        )
        target = output_dir / f"{step.label}.prompt.md"
        target.write_text(prompt, encoding="utf-8")
        previous_outputs.append(f"{step.label}: prompt compiled -> {target}")
        print(f"PROMPT_WRITTEN {target}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """
    `run` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `load_prompt_tooling()`, `load_bundle_or_report()`, `validate_bundle()`, `print_validation_issues()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        args: argparse가 전달한 서브커맨드 인자 네임스페이스다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    tooling = load_prompt_tooling()
    if tooling is None:
        return 1
    _, load_spec_bundle, validate_bundle, _, _ = tooling
    bundle = load_bundle_or_report(load_spec_bundle, args.spec_dir)
    if bundle is None:
        return 1
    issues = validate_bundle(bundle)
    if issues:
        print_validation_issues(issues)
        return 1

    project_id = resolve_project_id(args.project_id, args.spec_dir)
    workspace_path = resolve_workspace_path(args.workspace, project_id)
    request_body = bundle_to_request(
        project_id=project_id,
        bundle=bundle,
        workspace=workspace_path,
        rag_enabled=args.rag_enabled,
    )

    if args.backend_url:
        payload = json.dumps(request_body).encode("utf-8")
        request = urllib.request.Request(
            url=f"{args.backend_url.rstrip('/')}/api/v1/spec-runs",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request) as response:  # nosec
                print(response.read().decode("utf-8"))
                return 0
        except urllib.error.URLError as error:
            print(f"BACKEND_CALL_FAILED: {error}")
            return 1

    LocalSddRuntime = load_runtime_tooling()
    if LocalSddRuntime is None:
        return 1
    output_root = resolve_project_output_root(project_id)
    output_root.mkdir(parents=True, exist_ok=True)
    runtime = LocalSddRuntime(output_root=output_root)
    local_result = runtime.execute(
        project_id=project_id,
        bundle=bundle,
        workspace_path=workspace_path,
        rag_enabled=args.rag_enabled,
        runtime_mode=args.runtime,
    )
    print(
        json.dumps(
            {
                "runId": local_result.run_id,
                "status": local_result.status,
                "projectId": project_id,
                "runtime": args.runtime,
                "outputRoot": display_path(output_root),
                "workspace": display_path(local_result.workspace_dir),
                "promptDir": display_path(local_result.prompt_dir),
                "generatedFiles": local_result.generated_files,
                "results": [
                    {
                        "agent": result.agent,
                        "status": result.status,
                        "summary": result.summary,
                        "generatedFiles": result.generated_files,
                        "validations": result.validations,
                    }
                    for result in local_result.results
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if local_result.status in {"COMPLETED", "SIMULATED"} else 1


def cmd_setup(args: argparse.Namespace) -> int:
    """
    `setup` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_env_file()`, `ensure_codex_home()`, `load_env_values()`, `prompt_choice()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        args: argparse가 전달한 서브커맨드 인자 네임스페이스다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    ensure_env_file()
    ensure_codex_home()
    current_env = load_env_values(ENV_FILE)

    auth_mode = args.auth_mode or current_env.get("SPECYN_AUTH_MODE") or DEFAULT_SETUP_AUTH_MODE
    if not args.auth_mode and not args.non_interactive:
        auth_mode = prompt_choice(
            "인증 방식을 선택하세요.",
            [("chatgpt", "ChatGPT 계정 로그인"), ("openapi", "OpenAI API Key 사용")],
            default=auth_mode,
        )

    model = select_model(current_env.get("CODEX_MODEL") or current_env.get("OPENAI_MODEL"), args.model)
    use_browser_login = args.browser_login
    if auth_mode == "chatgpt" and not args.non_interactive:
        login_method = prompt_choice(
            "ChatGPT 로그인 방식을 선택하세요.",
            [("browser", "브라우저 로그인"), ("device", "장치 코드 로그인")],
            default="browser",
        )
        use_browser_login = login_method == "browser"

    updates = {
        "SPECYN_AUTH_MODE": auth_mode,
        "OPENAI_MODEL": model,
        "CODEX_MODEL": model,
        "CODEX_EXEC_MODE": "cli",
        "CODEX_COMMAND_TEMPLATE": "codex exec --json --model {model} --sandbox danger-full-access -C {workspace} --skip-git-repo-check",
        "CODEX_HOME": display_path(CODEX_HOME_DIR),
        "OPENAI_BASE_URL": current_env.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    }

    docker_cli = docker_cli_available()
    docker_ready, docker_detail = docker_daemon_status() if docker_cli else (False, "docker-not-installed")
    login_cached_before, login_status_before = codex_cached_login_hint()
    docker_verification_attempted = False
    docker_auth_applied = False
    warnings: list[str] = []

    openai_api_key = current_env.get("OPENAI_API_KEY", "")
    if auth_mode == "openapi":
        openai_api_key = resolve_openapi_key(
            current_env.get("OPENAI_API_KEY"),
            provided_api_key=args.api_key,
            non_interactive=args.non_interactive,
        )
        updates["OPENAI_API_KEY"] = openai_api_key

    write_env_updates(updates, ENV_FILE)

    install_codex = args.install_codex
    should_verify_docker = install_codex in {"auto", "yes"} and docker_ready
    if install_codex == "yes" and not docker_ready:
        print(
            "SETUP_FAILED: Docker agent 검증이 필요하지만 Docker Desktop/daemon 이 준비되지 않았습니다. "
            f"detail={docker_detail}"
        )
        return 1
    if install_codex in {"auto", "yes"} and not docker_ready:
        warnings.append(
            "Docker Desktop/daemon 이 준비되지 않아 agent/Codex 검증과 컨테이너 내부 인증을 건너뛰었습니다. "
            "Docker 실행 후 같은 명령을 다시 실행하면 검증을 마칠 수 있습니다."
        )

    codex_available = False
    codex_detail = "not-checked"
    if should_verify_docker:
        docker_verification_attempted = True
        codex_available, codex_detail = ensure_codex_in_agent(install_if_missing=install_codex != "no")
        if not codex_available:
            print(f"SETUP_FAILED: Docker agent 안에서 Codex를 확인하지 못했습니다. detail={codex_detail}")
            return 1

    if docker_ready and codex_available:
        login_cached_before, login_status_before = codex_login_status()
        if auth_mode == "openapi":
            if openai_api_key:
                codex_logout()
                if codex_login_with_api_key(openai_api_key) != 0:
                    print("SETUP_FAILED: Codex API key 로그인을 완료하지 못했습니다.")
                    return 1
                docker_auth_applied = True
            else:
                codex_logout()
                docker_auth_applied = True
        else:
            chatgpt_action = resolve_chatgpt_action(
                logged_in=login_cached_before,
                provided_action=args.chatgpt_action,
                non_interactive=args.non_interactive,
            )
            if chatgpt_action == "logout":
                codex_logout()
                docker_auth_applied = True
            elif chatgpt_action == "relogin":
                codex_logout()
                if codex_login_with_chatgpt(device_auth=not use_browser_login) != 0:
                    print("SETUP_FAILED: ChatGPT 계정 로그인을 완료하지 못했습니다.")
                    return 1
                docker_auth_applied = True
            else:
                docker_auth_applied = True
    elif auth_mode == "chatgpt" and args.chatgpt_action in {"logout", "relogin"}:
        warnings.append("Docker 준비 전에는 ChatGPT 로그아웃/재로그인을 실제로 수행할 수 없습니다.")
    elif auth_mode == "openapi":
        warnings.append("OPENAI_API_KEY 는 .env 에 저장되었지만 Docker agent 내부 Codex 로그인은 아직 적용되지 않았습니다.")

    summary = env_summary()
    summary["setupCompleted"] = True
    summary["dockerVerificationAttempted"] = docker_verification_attempted
    summary["dockerAuthApplied"] = docker_auth_applied
    summary["codexLoginStatusBefore"] = login_status_before
    if auth_mode == "chatgpt":
        summary["chatgptLoginMethod"] = "browser" if use_browser_login else "device"
    summary["warnings"] = warnings
    summary["nextCommands"] = [
        "python specyn.py auth-status",
        "python specyn.py doctor",
        "python specyn.py up -d",
        "python specyn.py sample-up -d",
    ]
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_auth_status(_: argparse.Namespace) -> int:
    """
    `auth_status` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_env_file()`, `ensure_codex_home()`, `env_summary()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        _: 작업을(를) 나타내는 `argparse.Namespace` 타입 입력값이다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    ensure_env_file()
    ensure_codex_home()
    print(json.dumps(env_summary(), ensure_ascii=False, indent=2))
    return 0


def cmd_up(args: argparse.Namespace) -> int:
    """
    `up` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_env_file()`, `ensure_codex_home()`, `ensure_docker_ready_for_command()`, `docker_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        args: argparse가 전달한 서브커맨드 인자 네임스페이스다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    ensure_env_file()
    ensure_codex_home()
    ready, _ = ensure_docker_ready_for_command("UP")
    if not ready:
        return 1
    command = [*docker_command("compose", "-f", DASHBOARD_COMPOSE_FILE), "up", "--build"]
    if args.detached:
        command.append("-d")
    completed = run_command(command, cwd=ROOT_DIR)
    return int(completed.returncode)


def cmd_down(args: argparse.Namespace) -> int:
    """
    `down` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_docker_ready_for_command()`, `docker_command()`, `run_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        args: argparse가 전달한 서브커맨드 인자 네임스페이스다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    ready, _ = ensure_docker_ready_for_command("DOWN")
    if not ready:
        return 1
    command = [*docker_command("compose", "-f", DASHBOARD_COMPOSE_FILE), "down"]
    if args.volumes:
        command.append("--volumes")
    completed = run_command(command, cwd=ROOT_DIR)
    return int(completed.returncode)


def cmd_sample_up(args: argparse.Namespace) -> int:
    """
    `sample_up` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_env_file()`, `ensure_codex_home()`, `ensure_docker_ready_for_command()`, `docker_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        args: argparse가 전달한 서브커맨드 인자 네임스페이스다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    if not SAMPLE_COMPOSE_FILE.exists():
        print(
            "SAMPLE_RUNTIME_NOT_GENERATED: projects/sample-service 런타임이 아직 생성되지 않았습니다. "
            "대시보드에서 Agent 실행으로 sample-service를 먼저 생성한 뒤 sample-up을 실행하세요."
        )
        return 1

    ensure_env_file()
    ensure_codex_home()
    ready, _ = ensure_docker_ready_for_command("SAMPLE_UP")
    if not ready:
        return 1
    command = [*docker_command("compose", "-f", SAMPLE_COMPOSE_FILE), "up", "--build"]
    if args.detached:
        command.append("-d")
    completed = run_command(command, cwd=ROOT_DIR)
    return int(completed.returncode)


def cmd_sample_down(args: argparse.Namespace) -> int:
    """
    `sample_down` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_docker_ready_for_command()`, `docker_command()`, `run_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        args: argparse가 전달한 서브커맨드 인자 네임스페이스다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    if not SAMPLE_COMPOSE_FILE.exists():
        print(
            "SAMPLE_RUNTIME_NOT_GENERATED: projects/sample-service 런타임이 아직 생성되지 않았습니다. "
            "중지할 sample-service 스택이 없습니다."
        )
        return 1

    ready, _ = ensure_docker_ready_for_command("SAMPLE_DOWN")
    if not ready:
        return 1
    command = [*docker_command("compose", "-f", SAMPLE_COMPOSE_FILE), "down"]
    if args.volumes:
        command.append("--volumes")
    completed = run_command(command, cwd=ROOT_DIR)
    return int(completed.returncode)


def cmd_doctor(_: argparse.Namespace) -> int:
    """
    `doctor` 서브커맨드의 실제 실행 로직을 수행한다.

    주요 흐름은 `command_report()`, `which()`, `repo_local_gradle()`, `repo_venv_python()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        _: 작업을(를) 나타내는 `argparse.Namespace` 타입 입력값이다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    report: dict[str, dict[str, Any]] = {
        "python": command_report([sys.executable, "--version"], source="current-interpreter")
    }
    standard_commands = {
        "java": ["java", "-version"],
        "node": ["node", "-v"],
        "npm": ["npm", "-v"],
        "codex": ["codex", "--help"],
        "docker": ["docker", "--version"],
    }
    for name, command in standard_commands.items():
        binary = command[0]
        if shutil.which(binary) is None:
            report[name] = {"available": False}
            continue
        report[name] = command_report(command, source="system")

    local_gradle = repo_local_gradle()
    if local_gradle is not None:
        report["gradle"] = command_report([str(local_gradle), "-v"], source="repo-local")
    elif shutil.which("gradle") is not None:
        report["gradle"] = command_report(["gradle", "-v"], source="system")
    else:
        report["gradle"] = {"available": False}

    report["venv"] = {
        "available": repo_venv_python() is not None,
        "python": str(repo_venv_python()) if repo_venv_python() is not None else None,
    }
    env_values = load_env_values(ENV_FILE) if ENV_FILE.exists() else {}
    report["specynEnv"] = {
        "available": ENV_FILE.exists(),
        "path": display_path(ENV_FILE),
        "authMode": env_values.get("SPECYN_AUTH_MODE", DEFAULT_SETUP_AUTH_MODE) if ENV_FILE.exists() else None,
        "apiKeyConfigured": bool(env_values.get("OPENAI_API_KEY", "").strip()) if ENV_FILE.exists() else False,
        "model": env_values.get("CODEX_MODEL", DEFAULT_SETUP_MODEL) if ENV_FILE.exists() else None,
    }

    docker_cli = docker_cli_available()
    docker_ready, docker_detail = docker_daemon_status() if docker_cli else (False, "docker-not-installed")
    report["dockerDaemon"] = {
        "available": docker_cli,
        "ready": docker_ready,
        "status": docker_detail,
    }

    cached_login, cached_detail = codex_cached_login_hint()
    report["codexCache"] = {
        "available": True,
        "path": display_path(CODEX_AUTH_FILE),
        "loggedIn": cached_login,
        "status": cached_detail,
    }

    if docker_ready and DASHBOARD_COMPOSE_FILE.exists():
        available, detail = ensure_codex_in_agent(install_if_missing=False)
        report["dockerAgent"] = {
            "available": available,
            "composeFile": display_path(DASHBOARD_COMPOSE_FILE),
            "service": DASHBOARD_AGENT_SERVICE,
            "version": detail,
        }
        if available:
            logged_in, login_detail = codex_login_status()
            report["dockerAgentAuth"] = {
                "available": True,
                "loggedIn": logged_in,
                "status": login_detail,
            }
        else:
            report["dockerAgentAuth"] = {
                "available": False,
                "loggedIn": False,
                "status": detail,
            }
    else:
        reason = "compose-file-missing" if not DASHBOARD_COMPOSE_FILE.exists() else docker_detail
        report["dockerAgent"] = {
            "available": False,
            "composeFile": display_path(DASHBOARD_COMPOSE_FILE),
            "service": DASHBOARD_AGENT_SERVICE,
            "version": reason,
        }
        report["dockerAgentAuth"] = {
            "available": False,
            "loggedIn": cached_login,
            "status": reason,
        }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    """
    도구 계층에서 CLI 인자 파서를 구성한다.

    주요 흐름은 `ArgumentParser()`, `add_subparsers()`, `add_parser()`, `add_argument()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        함수에서 조립한 `argparse.ArgumentParser` 타입 결과다.
    """
    parser = argparse.ArgumentParser(description="Specyn CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="spec bundle 검증")
    validate_parser.add_argument("--spec-dir", required=True)
    validate_parser.set_defaults(func=cmd_validate)

    init_parser = subparsers.add_parser("init-spec", help="spec 템플릿 복사")
    init_parser.add_argument("--project-id", required=True)
    init_parser.add_argument("--output-dir", required=True)
    init_parser.add_argument("--overwrite", action="store_true")
    init_parser.set_defaults(func=cmd_init_spec)

    compile_parser = subparsers.add_parser("compile-prompts", help="agent prompt 파일 생성")
    compile_parser.add_argument("--spec-dir", required=True)
    compile_parser.add_argument("--project-id")
    compile_parser.add_argument("--output-dir", default=str(PROMPT_ROOT_DIR))
    compile_parser.add_argument("--workspace")
    compile_parser.add_argument("--rag-enabled", action="store_true")
    compile_parser.set_defaults(func=cmd_compile_prompts)

    run_parser = subparsers.add_parser("run", help="backend 호출 또는 로컬 SDD 실행")
    run_parser.add_argument("--spec-dir", required=True)
    run_parser.add_argument("--project-id")
    run_parser.add_argument("--workspace")
    run_parser.add_argument("--backend-url")
    run_parser.add_argument("--rag-enabled", action="store_true")
    run_parser.add_argument(
        "--runtime",
        choices=("local", "simulate"),
        default="local",
        help="backend-url 없이 실행할 때 사용할 로컬 런타임 모드",
    )
    run_parser.set_defaults(func=cmd_run)

    setup_parser = subparsers.add_parser("setup", help=".env 기반 초기 설정과 Docker agent 인증 구성")
    setup_parser.add_argument("--auth-mode", choices=("chatgpt", "openapi"))
    setup_parser.add_argument("--model")
    setup_parser.add_argument("--api-key")
    setup_parser.add_argument("--chatgpt-action", choices=("reuse", "relogin", "logout"))
    setup_parser.add_argument(
        "--install-codex",
        choices=("auto", "yes", "no"),
        default="auto",
        help="Docker agent 안의 Codex 설치 검증 및 필요 시 이미지 빌드 여부",
    )
    setup_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="질문 없이 현재 .env 또는 전달된 옵션만 사용",
    )
    setup_parser.add_argument(
        "--browser-login",
        action="store_true",
        help="ChatGPT 로그인 시 device code 대신 기본 브라우저 플로우 사용",
    )
    setup_parser.set_defaults(func=cmd_setup)

    auth_status_parser = subparsers.add_parser("auth-status", help="현재 인증/.env 상태 확인")
    auth_status_parser.set_defaults(func=cmd_auth_status)

    up_parser = subparsers.add_parser("up", help="dashboard 전체 스택을 Docker Compose로 실행")
    up_parser.add_argument("-d", "--detached", action="store_true")
    up_parser.set_defaults(func=cmd_up)

    down_parser = subparsers.add_parser("down", help="dashboard 전체 스택을 중지")
    down_parser.add_argument("--volumes", action="store_true")
    down_parser.set_defaults(func=cmd_down)

    sample_up_parser = subparsers.add_parser("sample-up", help="sample-service 스택을 Docker Compose로 실행")
    sample_up_parser.add_argument("-d", "--detached", action="store_true")
    sample_up_parser.set_defaults(func=cmd_sample_up)

    sample_down_parser = subparsers.add_parser("sample-down", help="sample-service 스택을 중지")
    sample_down_parser.add_argument("--volumes", action="store_true")
    sample_down_parser.set_defaults(func=cmd_sample_down)

    doctor_parser = subparsers.add_parser("doctor", help="로컬 실행 환경 점검")
    doctor_parser.set_defaults(func=cmd_doctor)
    return parser


def main() -> int:
    """
    도구 계층에서 메인 진입점 역할을 수행한다.

    주요 흐름은 `build_parser()`, `parse_args()`, `should_reexec_into_repo_venv()`, `reexec_into_repo_venv()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    parser = build_parser()
    args = parser.parse_args()
    if should_reexec_into_repo_venv(args.command):
        reexec_into_repo_venv()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
