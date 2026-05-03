"""
로컬 개발과 CI 보조 작업을 하나의 CLI로 묶은 태스크 러너 모듈이다.
가상환경 준비, 프런트엔드/백엔드 실행, 샘플 프로젝트 생성 여부 확인, Docker·Gradle·npm 의존성 점검까지 개발 편의성에 필요한 절차를 단계별 함수로 나눠 제공한다.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile

ROOT_DIR = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT_DIR / "dashboard"
PROJECTS_DIR = ROOT_DIR / "projects"
BACKEND_DIR = DASHBOARD_DIR / "backend"
FRONTEND_DIR = DASHBOARD_DIR / "frontend"
AI_SERVER_DIR = DASHBOARD_DIR / "ai-server"
SAMPLE_PROJECT_DIR = PROJECTS_DIR / "sample-service"
SAMPLE_BACKEND_DIR = SAMPLE_PROJECT_DIR / "backend"
SAMPLE_FRONTEND_DIR = SAMPLE_PROJECT_DIR / "frontend"
SAMPLE_AI_SERVER_DIR = SAMPLE_PROJECT_DIR / "ai-server"
VENV_DIR = ROOT_DIR / ".venv"
VENV_PYTHON = VENV_DIR / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
SPECYN_ENTRYPOINT = ROOT_DIR / "specyn.py"
LOCAL_TOOL_DIR = ROOT_DIR / ".specyn" / "tools"
LOCAL_GRADLE_VERSION = os.environ.get("SPECYN_GRADLE_VERSION", "8.14")
LOCAL_GRADLE_DIR = LOCAL_TOOL_DIR / f"gradle-{LOCAL_GRADLE_VERSION}"
LOCAL_GRADLE_ARCHIVE = LOCAL_TOOL_DIR / f"gradle-{LOCAL_GRADLE_VERSION}-bin.zip"
WINDOWS_SHELL_EXTENSIONS = {".cmd", ".bat"}
NPM_PUBLIC_REGISTRY = "https://registry.npmjs.org/"
NPM_PUBLIC_MIRROR_MARKER = "/artifactory/api/npm/npm-public/"
DEV_READY_TIMEOUT_SECONDS = 180
DEV_READY_POLL_INTERVAL_SECONDS = 1


class TaskError(RuntimeError):
    """
    스크립트 계층에서 사용되는 `TaskError` 클래스다.

    상속 기반은 `RuntimeError`이다.
    """
    pass


def prefixed(message: str) -> str:
    """
    스크립트 계층에서 `prefixed()`가 맡는 작업 관련 작업을 수행한다.

    외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

    Args:
        message: 출력하거나 전달할 메시지 문자열이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return f"[specyn] {message}"


def exit_with(message: str, code: int = 1) -> int:
    """
    스크립트 계층에서 `exit_with()`가 맡는 with 관련 작업을 수행한다.

    주요 흐름은 `prefixed()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        message: 출력하거나 전달할 메시지 문자열이다.
        code: 종료 코드나 상태 코드 값이다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    print(prefixed(message), file=sys.stderr)
    return code


def is_windows() -> bool:
    """
    스크립트 계층에서 windows 여부를 판단한다.

    외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    return os.name == "nt"


def format_command(command: list[str]) -> str:
    """
    스크립트 계층에서 command을(를) 실행/표시용 문자열로 정리한다.

    주요 흐름은 `is_windows()`, `list2cmdline()`, `quote()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    if is_windows():
        return subprocess.list2cmdline(command)
    return " ".join(shlex.quote(part) for part in command)


def clean_env() -> dict[str, str]:
    """
    스크립트 계층에서 환경 변수을(를) 불필요한 값 없이 정제한다.

    주요 흐름은 `pop()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    env = os.environ.copy()
    remove_keys = [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "http_proxy",
        "https_proxy",
        "ALL_PROXY",
        "all_proxy",
        "NPM_CONFIG_REGISTRY",
        "npm_config_registry",
        "NODE_OPTIONS",
        "NODE_EXTRA_CA_CERTS",
    ]
    for key in remove_keys:
        env.pop(key, None)
    env["NPM_CONFIG_REGISTRY"] = NPM_PUBLIC_REGISTRY.rstrip("/")
    return env


def rewrite_npm_resolved_url(url: str) -> str:
    """
    스크립트 계층에서 npm resolved URL을(를) 새로운 규칙에 맞게 다시 쓴다.

    주요 흐름은 `startswith()`, `partition()`, `lstrip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        url: 상태 확인이나 호출에 사용할 URL이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    if url.startswith(NPM_PUBLIC_REGISTRY):
        return url
    if NPM_PUBLIC_MIRROR_MARKER in url:
        _, _, package_path = url.partition(NPM_PUBLIC_MIRROR_MARKER)
        return f"{NPM_PUBLIC_REGISTRY}{package_path.lstrip('/')}"
    return url


def sanitize_npm_lockfile(lockfile_path: Path | None = None) -> int:
    """
    스크립트 계층에서 npm lockfile을(를) 안전하고 일관된 상태로 정리한다.

    주요 흐름은 `rewrite_npm_resolved_url()`, `prefixed()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        lockfile_path: 정리할 npm lockfile 경로다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    path = lockfile_path or FRONTEND_DIR / "package-lock.json"
    if not path.exists():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    packages = data.get("packages")
    if not isinstance(packages, dict):
        return 0
    rewritten_entries = 0
    for metadata in packages.values():
        if not isinstance(metadata, dict):
            continue
        resolved = metadata.get("resolved")
        if not isinstance(resolved, str):
            continue
        rewritten = rewrite_npm_resolved_url(resolved)
        if rewritten == resolved:
            continue
        metadata["resolved"] = rewritten
        rewritten_entries += 1
    if rewritten_entries:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(prefixed(f"npm lockfile registry 정리 완료 ({rewritten_entries} entries)"))
    return rewritten_entries


def frontend_npm_install_command(frontend_dir: Path = FRONTEND_DIR) -> list[str]:
    """
    스크립트 계층에서 `frontend_npm_install_command()`가 맡는 npm install command 관련 작업을 수행한다.

    주요 흐름은 `exists()`, `rstrip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        frontend_dir: 파일 시스템 경로 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    lockfile = frontend_dir / "package-lock.json"
    base_command = ["npm", "ci" if lockfile.exists() else "install"]
    return [
        *base_command,
        f"--registry={NPM_PUBLIC_REGISTRY.rstrip('/')}",
        "--include=optional",
        "--no-audit",
        "--no-fund",
    ]


def system_python_cmd() -> list[str]:
    """
    스크립트 계층에서 `system_python_cmd()`가 맡는 Python cmd 관련 작업을 수행한다.

    주요 흐름은 `is_windows()`, `which()`, `TaskError()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    candidates: list[list[str]] = []
    if sys.executable:
        candidates.append([sys.executable])
    if is_windows():
        candidates.extend([["python"], ["py", "-3"]])
    else:
        candidates.extend([["python3"], ["python"]])
    seen: set[tuple[str, ...]] = set()
    for candidate in candidates:
        key = tuple(candidate)
        if key in seen:
            continue
        seen.add(key)
        executable = candidate[0]
        if executable == sys.executable or shutil.which(executable):
            return candidate
    raise TaskError("Python 3.12+를 찾을 수 없습니다.")


def venv_python_cmd() -> list[str]:
    """
    스크립트 계층에서 `venv_python_cmd()`가 맡는 Python cmd 관련 작업을 수행한다.

    주요 흐름은 `system_python_cmd()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    if VENV_PYTHON.exists():
        return [str(VENV_PYTHON)]
    return system_python_cmd()


def local_gradle_executable() -> Path:
    """
    스크립트 계층에서 `local_gradle_executable()`가 맡는 Gradle executable 관련 작업을 수행한다.

    주요 흐름은 `is_windows()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    executable = "gradle.bat" if is_windows() else "gradle"
    return LOCAL_GRADLE_DIR / "bin" / executable


def prepare_command_for_subprocess(command: list[str]) -> list[str]:
    """
    스크립트 계층에서 `prepare_command_for_subprocess()`가 맡는 command for 하위 프로세스 관련 작업을 수행한다.

    주요 흐름은 `TaskError()`, `is_windows()`, `which()`, `is_file()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    if not command:
        raise TaskError("실행할 명령이 비어 있습니다.")
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


def run_checked(command: list[str], *, cwd: Path | None = None, extra_env: dict[str, str] | None = None) -> None:
    """
    스크립트 계층에서 checked을(를) 실제로 실행한다.

    주요 흐름은 `clean_env()`, `prepare_command_for_subprocess()`, `run()`, `TaskError()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.
        cwd: 외부 명령을 실행할 현재 작업 디렉터리다.
        extra_env: 키-값 형태의 매핑 입력값이다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    env = clean_env()
    if extra_env:
        env.update(extra_env)
    working_dir = cwd or ROOT_DIR
    prepared_command = prepare_command_for_subprocess(command)
    completed = subprocess.run(prepared_command, cwd=working_dir, env=env)
    if completed.returncode != 0:
        raise TaskError(f"명령 실행 실패: {format_command(prepared_command)} (exit={completed.returncode})")


def ensure_command_available(binary: str, *, purpose: str) -> None:
    """
    스크립트 계층에서 command available이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `which()`, `TaskError()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        binary: 문자열 입력값이다.
        purpose: 문자열 입력값이다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    if shutil.which(binary) is None:
        raise TaskError(f"`{binary}` 명령을 찾을 수 없습니다. {purpose}")


def ensure_env_file() -> None:
    """
    스크립트 계층에서 환경 변수 파일이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `copy2()`, `prefixed()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    env_example = ROOT_DIR / ".env.example"
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        shutil.copy2(env_example, env_file)
        print(prefixed(".env.example -> .env 복사 완료"))


def ensure_runtime_dirs() -> None:
    """
    스크립트 계층에서 런타임 dirs이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `mkdir()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.
    """
    for path in [
        ROOT_DIR / ".workspace",
        ROOT_DIR / ".specyn" / "prompts",
        LOCAL_TOOL_DIR,
        ROOT_DIR / "specs" / "projects",
        DASHBOARD_DIR,
        PROJECTS_DIR,
        SAMPLE_PROJECT_DIR / "docs",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def sample_runtime_required_files() -> list[Path]:
    """
    스크립트 계층에서 `sample_runtime_required_files()`가 맡는 런타임 required 파일 목록 관련 작업을 수행한다.

    외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    return [
        SAMPLE_FRONTEND_DIR / "package.json",
        SAMPLE_FRONTEND_DIR / "src" / "App.tsx",
        SAMPLE_BACKEND_DIR / "build.gradle.kts",
        SAMPLE_BACKEND_DIR / "src" / "main" / "resources" / "application.yml",
        SAMPLE_AI_SERVER_DIR / "app" / "main.py",
        SAMPLE_AI_SERVER_DIR / "requirements.txt",
    ]


def sample_runtime_is_generated() -> bool:
    """
    스크립트 계층에서 `sample_runtime_is_generated()`가 맡는 런타임 is 생성 산출물 관련 작업을 수행한다.

    주요 흐름은 `sample_runtime_required_files()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    return all(path.exists() for path in sample_runtime_required_files())


def ensure_sample_runtime_generated() -> None:
    """
    스크립트 계층에서 sample-service 런타임 생성 산출물이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `sample_runtime_is_generated()`, `prefixed()`, `run_specyn()`, `sample_runtime_required_files()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    if sample_runtime_is_generated():
        return
    print(prefixed("sample-service 런타임이 없어 spec 기반 생성 절차를 자동 실행합니다."))
    run_specyn([
        "run",
        "--spec-dir",
        "specs/001-sample-service",
        "--project-id",
        "sample-service",
        "--workspace",
        ".workspace/sample-service",
    ])
    missing = [str(path) for path in sample_runtime_required_files() if not path.exists()]
    if missing:
        raise TaskError(f"sample-service 런타임 생성이 완료되지 않았습니다: {missing}")


def ensure_frontend_dependencies(frontend_dir: Path, *, label: str) -> None:
    """
    스크립트 계층에서 프런트엔드 dependencies이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `TaskError()`, `sanitize_npm_lockfile()`, `prefixed()`, `run_checked()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        frontend_dir: 파일 시스템 경로 객체다.
        label: 문자열 입력값이다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        raise TaskError(f"{label} package.json 이 없습니다: {package_json}")
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        return
    lockfile = frontend_dir / "package-lock.json"
    if lockfile.exists():
        sanitize_npm_lockfile(lockfile)
    print(prefixed(f"{label} 의 Node.js 의존성을 설치합니다."))
    run_checked(frontend_npm_install_command(frontend_dir), cwd=frontend_dir)


def gradle_distribution_url() -> str:
    """
    스크립트 계층에서 `gradle_distribution_url()`가 맡는 distribution URL 관련 작업을 수행한다.

    외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return f"https://services.gradle.org/distributions/gradle-{LOCAL_GRADLE_VERSION}-bin.zip"


def ensure_local_gradle() -> Path:
    """
    스크립트 계층에서 로컬 Gradle이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `local_gradle_executable()`, `is_windows()`, `chmod()`, `stat()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    gradle_path = local_gradle_executable()
    if gradle_path.exists():
        if not is_windows():
            gradle_path.chmod(gradle_path.stat().st_mode | 0o111)
        return gradle_path

    archive_path = LOCAL_GRADLE_ARCHIVE
    extract_dir = LOCAL_TOOL_DIR / f".gradle-{LOCAL_GRADLE_VERSION}-extract"
    extracted_root = extract_dir / f"gradle-{LOCAL_GRADLE_VERSION}"

    if extract_dir.exists():
        shutil.rmtree(extract_dir, ignore_errors=True)
    extract_dir.mkdir(parents=True, exist_ok=True)

    print(prefixed(f"Gradle {LOCAL_GRADLE_VERSION} 로컬 배포판을 준비합니다."))
    try:
        with (urllib.request.urlopen(gradle_distribution_url()) as response, archive_path.open("wb") as output):
            shutil.copyfileobj(response, output)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_dir)
        if not extracted_root.exists():
            raise TaskError(f"Gradle 압축 해제 결과를 찾을 수 없습니다: {extracted_root}")
        if LOCAL_GRADLE_DIR.exists():
            shutil.rmtree(LOCAL_GRADLE_DIR, ignore_errors=True)
        shutil.move(str(extracted_root), str(LOCAL_GRADLE_DIR))
        gradle_path = local_gradle_executable()
        if not gradle_path.exists():
            raise TaskError(f"로컬 Gradle 실행 파일을 찾을 수 없습니다: {gradle_path}")
        if not is_windows():
            gradle_path.chmod(gradle_path.stat().st_mode | 0o111)
    except TaskError:
        if LOCAL_GRADLE_DIR.exists():
            shutil.rmtree(LOCAL_GRADLE_DIR, ignore_errors=True)
        raise
    except Exception as error:  # pragma: no cover
        if LOCAL_GRADLE_DIR.exists():
            shutil.rmtree(LOCAL_GRADLE_DIR, ignore_errors=True)
        raise TaskError(f"로컬 Gradle 준비 실패: {error}") from error
    finally:
        if archive_path.exists():
            archive_path.unlink(missing_ok=True)
        if extract_dir.exists():
            shutil.rmtree(extract_dir, ignore_errors=True)

    print(prefixed(f"로컬 Gradle 준비 완료: {gradle_path}"))
    return gradle_path


def maybe_bootstrap_gradle() -> None:
    """
    스크립트 계층에서 `maybe_bootstrap_gradle()`가 맡는 bootstrap Gradle 관련 작업을 수행한다.

    주요 흐름은 `prefixed()`, `local_gradle_executable()`, `which()`, `ensure_local_gradle()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    """
    if os.environ.get("SPECYN_SKIP_GRADLE_BOOTSTRAP") == "1":
        print(prefixed("SPECYN_SKIP_GRADLE_BOOTSTRAP=1 이므로 로컬 Gradle 준비를 건너뜁니다."))
        return
    if local_gradle_executable().exists() or shutil.which("gradle"):
        return
    try:
        ensure_local_gradle()
    except TaskError as error:
        print(prefixed(f"{error} 로컬 전체 스택 실행 시에는 시스템 Gradle 8.14+ 또는 Docker가 추가로 필요할 수 있습니다."), file=sys.stderr)


def resolve_gradle_command(backend_dir: Path = BACKEND_DIR) -> list[str]:
    """
    스크립트 계층에서 Gradle command의 최종 값을 결정한다.

    주요 흐름은 `local_gradle_executable()`, `which()`, `is_windows()`, `TaskError()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        backend_dir: 파일 시스템 경로 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    local_gradle = local_gradle_executable()
    if local_gradle.exists():
        return [str(local_gradle)]
    if shutil.which("gradle"):
        return ["gradle"]
    wrapper = backend_dir / ("gradlew.bat" if is_windows() else "gradlew")
    if wrapper.exists():
        return [str(wrapper)]
    raise TaskError("Gradle 실행 경로를 찾을 수 없습니다. 먼저 bootstrap으로 로컬 Gradle 준비를 시도하거나 시스템 Gradle 8.14+ 또는 Docker를 설치하세요.")


def backend_bootrun_command(backend_dir: Path = BACKEND_DIR) -> list[str]:
    """
    스크립트 계층에서 `backend_bootrun_command()`가 맡는 bootrun command 관련 작업을 수행한다.

    주요 흐름은 `resolve_gradle_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        backend_dir: 파일 시스템 경로 객체다.

    Returns:
        조건에 맞춰 수집하거나 정렬한 목록이다.
    """
    return [*resolve_gradle_command(backend_dir), "--console=plain", "--no-daemon", "--quiet", "bootRun"]


def ensure_gradle_runtime(backend_dir: Path) -> None:
    """
    스크립트 계층에서 Gradle 런타임이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `local_gradle_executable()`, `which()`, `ensure_local_gradle()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        backend_dir: 파일 시스템 경로 객체다.
    """
    local_gradle = local_gradle_executable()
    if local_gradle.exists() or shutil.which("gradle"):
        return
    wrapper_dir = backend_dir / "gradle" / "wrapper"
    if (wrapper_dir / "gradle-wrapper.jar").exists() and (wrapper_dir / "gradle-wrapper.properties").exists():
        return
    ensure_local_gradle()


def service_responding(url: str, *, timeout: float = 2.0) -> bool:
    """
    스크립트 계층에서 `service_responding()`가 맡는 responding 관련 작업을 수행한다.

    주요 흐름은 `Request()`, `urlopen()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        url: 상태 확인이나 호출에 사용할 URL이다.
        timeout: 외부 명령을 기다릴 최대 시간(초)이다.

    Returns:
        조건 충족 여부를 나타내는 불리언 값이다.
    """
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return 200 <= getattr(response, "status", 200) < 500
    except urllib.error.HTTPError as exc:
        return 200 <= exc.code < 500
    except Exception:
        return False


def ensure_processes_running(processes: list[tuple[str, subprocess.Popen[bytes]]]) -> None:
    """
    스크립트 계층에서 프로세스 목록 running이(가) 준비되었는지 확인하고 부족하면 보완한다.

    주요 흐름은 `poll()`, `TaskError()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        processes: 동시에 관리 중인 프로세스 목록이다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    for name, process in processes:
        return_code = process.poll()
        if return_code is None:
            continue
        if return_code == 0:
            raise TaskError(f"{name} 프로세스가 종료되어 dev 모드를 중단합니다.")
        raise TaskError(f"{name} 프로세스가 비정상 종료되었습니다. exit={return_code}")


def wait_for_dev_services(processes: list[tuple[str, subprocess.Popen[bytes]]]) -> None:
    """
    스크립트 계층에서 for 개발 서비스 목록이(가) 준비될 때까지 대기한다.

    주요 흐름은 `monotonic()`, `ensure_processes_running()`, `service_responding()`, `prefixed()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        processes: 동시에 관리 중인 프로세스 목록이다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    service_targets = {
        "Dashboard AI Server": "http://127.0.0.1:8100/health",
        "Dashboard Backend": "http://127.0.0.1:8180/api/v1/spec-runs/health",
        "Dashboard Frontend": "http://127.0.0.1:4173/",
    }
    ready_services: set[str] = set()
    deadline = time.monotonic() + DEV_READY_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        ensure_processes_running(processes)
        for name, url in service_targets.items():
            if name in ready_services:
                continue
            if service_responding(url):
                ready_services.add(name)
                print(prefixed(f"{name} 준비 완료: {url}"))
        if len(ready_services) == len(service_targets):
            print(prefixed("모든 대시보드 개발 서버 준비 완료: Frontend=http://localhost:4173, Backend=http://localhost:8180, AI Server=http://localhost:8100 (종료는 Ctrl+C)"))
            return
        time.sleep(DEV_READY_POLL_INTERVAL_SECONDS)
    pending = ", ".join(name for name in service_targets if name not in ready_services)
    raise TaskError(f"dev 준비 시간 초과: {pending} 상태를 확인하지 못했습니다. 위 로그와 포트(4173/8100/8180) 점유 상태를 확인하세요.")


def wait_for_sample_services(processes: list[tuple[str, subprocess.Popen[bytes]]]) -> None:
    """
    스크립트 계층에서 for sample-service 서비스 목록이(가) 준비될 때까지 대기한다.

    주요 흐름은 `monotonic()`, `ensure_processes_running()`, `service_responding()`, `prefixed()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        processes: 동시에 관리 중인 프로세스 목록이다.

    Raises:
        TaskError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
    """
    service_targets = {
        "Sample AI Server": "http://127.0.0.1:8000/health",
        "Sample Backend": "http://127.0.0.1:8080/api/v1/generated/sample-service/summary",
        "Sample Frontend": "http://127.0.0.1:5173/",
    }
    ready_services: set[str] = set()
    deadline = time.monotonic() + DEV_READY_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        ensure_processes_running(processes)
        for name, url in service_targets.items():
            if name in ready_services:
                continue
            if service_responding(url):
                ready_services.add(name)
                print(prefixed(f"{name} 준비 완료: {url}"))
        if len(ready_services) == len(service_targets):
            print(prefixed("sample-service 런타임 준비 완료: Frontend=http://localhost:5173, Backend=http://localhost:8080, AI Server=http://localhost:8000 (종료는 Ctrl+C)"))
            return
        time.sleep(DEV_READY_POLL_INTERVAL_SECONDS)
    pending = ", ".join(name for name in service_targets if name not in ready_services)
    raise TaskError(f"sample-dev 준비 시간 초과: {pending} 상태를 확인하지 못했습니다. 위 로그와 포트(5173/8000/8080) 점유 상태를 확인하세요.")


def run_specyn(command: list[str]) -> None:
    """
    스크립트 계층에서 specyn을(를) 실제로 실행한다.

    주요 흐름은 `run_checked()`, `venv_python_cmd()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.
    """
    run_checked([*venv_python_cmd(), str(SPECYN_ENTRYPOINT), *command], cwd=ROOT_DIR)


def task_bootstrap() -> None:
    """
    `bootstrap` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_env_file()`, `ensure_runtime_dirs()`, `run_checked()`, `system_python_cmd()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    """
    ensure_env_file()
    ensure_runtime_dirs()
    if not VENV_PYTHON.exists():
        run_checked([*system_python_cmd(), "-m", "venv", str(VENV_DIR)], cwd=ROOT_DIR)
    run_checked([*venv_python_cmd(), "-m", "pip", "install", "--upgrade", "pip"], cwd=ROOT_DIR)
    run_checked([*venv_python_cmd(), "-m", "pip", "install", "-r", "dashboard/ai-server/requirements.txt", "-r", "dashboard/ai-server/requirements-dev.txt", "-r", "tools/requirements.txt"], cwd=ROOT_DIR)
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    sanitize_npm_lockfile(FRONTEND_DIR / "package-lock.json")
    run_checked(frontend_npm_install_command(FRONTEND_DIR), cwd=FRONTEND_DIR)
    if (SAMPLE_FRONTEND_DIR / "package.json").exists():
        ensure_frontend_dependencies(SAMPLE_FRONTEND_DIR, label="sample-service frontend")
    else:
        print(prefixed("sample-service frontend scaffold가 아직 없어 bootstrap 단계에서는 건너뜁니다."))
    maybe_bootstrap_gradle()
    print(prefixed("bootstrap 완료"))


def task_doctor() -> None:
    """
    `doctor` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `venv_python_cmd()`, `system_python_cmd()`, `run_checked()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    python_command = [*venv_python_cmd(), str(SPECYN_ENTRYPOINT), "doctor"] if VENV_PYTHON.exists() else [*system_python_cmd(), str(SPECYN_ENTRYPOINT), "doctor"]
    run_checked(python_command, cwd=ROOT_DIR)


def task_up() -> None:
    """
    `up` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_command_available()`, `run_checked()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    ensure_command_available("docker", purpose="Docker Desktop 또는 Docker Engine + Compose v2를 설치하세요.")
    run_checked(["docker", "compose", "-f", "docker-compose.local.yml", "up", "--build"], cwd=ROOT_DIR)


def task_ai_server() -> None:
    """
    `ai_server` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `run_checked()`, `venv_python_cmd()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    run_checked([*venv_python_cmd(), "-m", "uvicorn", "app.main:app", "--app-dir", "dashboard/ai-server", "--host", "0.0.0.0", "--port", "8100"], cwd=ROOT_DIR)


def task_backend() -> None:
    """
    `backend` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_gradle_runtime()`, `run_checked()`, `backend_bootrun_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    ensure_gradle_runtime(BACKEND_DIR)
    run_checked(backend_bootrun_command(BACKEND_DIR), cwd=BACKEND_DIR)


def task_frontend() -> None:
    """
    `frontend` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_command_available()`, `run_checked()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    run_checked(["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4173"], cwd=FRONTEND_DIR)


def task_sample_ai_server() -> None:
    """
    `sample_ai_server` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_sample_runtime_generated()`, `run_checked()`, `venv_python_cmd()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    ensure_sample_runtime_generated()
    run_checked([*venv_python_cmd(), "-m", "uvicorn", "app.main:app", "--app-dir", "projects/sample-service/ai-server", "--host", "0.0.0.0", "--port", "8000"], cwd=ROOT_DIR)


def task_sample_backend() -> None:
    """
    `sample_backend` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_sample_runtime_generated()`, `ensure_gradle_runtime()`, `run_checked()`, `backend_bootrun_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    ensure_sample_runtime_generated()
    ensure_gradle_runtime(SAMPLE_BACKEND_DIR)
    run_checked(backend_bootrun_command(SAMPLE_BACKEND_DIR), cwd=SAMPLE_BACKEND_DIR)


def task_sample_frontend() -> None:
    """
    `sample_frontend` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_command_available()`, `ensure_sample_runtime_generated()`, `ensure_frontend_dependencies()`, `run_checked()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    ensure_sample_runtime_generated()
    ensure_frontend_dependencies(SAMPLE_FRONTEND_DIR, label="sample-service frontend")
    run_checked(["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"], cwd=SAMPLE_FRONTEND_DIR)


def terminate_process(process: subprocess.Popen[bytes]) -> None:
    """
    스크립트 계층에서 프로세스을(를) 종료한다.

    주요 흐름은 `poll()`, `is_windows()`, `send_signal()`, `wait()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

    Args:
        process: 프로세스을(를) 나타내는 `subprocess.Popen[bytes]` 타입 입력값이다.
    """
    if process.poll() is not None:
        return
    try:
        if is_windows():
            try:
                process.send_signal(signal.CTRL_BREAK_EVENT)
                process.wait(timeout=5)
                return
            except (subprocess.TimeoutExpired, Exception):
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
                process.wait(timeout=5)
                return
        process.terminate()
        process.wait(timeout=5)
    except Exception:
        process.kill()
        process.wait(timeout=5)


def start_process(name: str, command: list[str], cwd: Path) -> tuple[str, subprocess.Popen[bytes]]:
    """
    스크립트 계층에서 프로세스을(를) 시작한다.

    주요 흐름은 `prepare_command_for_subprocess()`, `is_windows()`, `Popen()`, `prefixed()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        name: 문자열 입력값이다.
        command: 실행 파일과 인자를 순서대로 담은 명령 리스트다.
        cwd: 외부 명령을 실행할 현재 작업 디렉터리다.

    Returns:
        함수에서 조립한 `tuple[str, subprocess.Popen[bytes]]` 타입 결과다.
    """
    prepared_command = prepare_command_for_subprocess(command)
    creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if is_windows() else 0
    process = subprocess.Popen(prepared_command, cwd=cwd, creationflags=creationflags)
    print(prefixed(f"{name} 시작: {format_command(prepared_command)}"))
    return name, process


def task_dev() -> None:
    """
    `dev` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_command_available()`, `ensure_gradle_runtime()`, `start_process()`, `venv_python_cmd()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.
    """
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    processes: list[tuple[str, subprocess.Popen[bytes]]] = []
    try:
        ensure_gradle_runtime(BACKEND_DIR)
        processes.append(start_process("Dashboard AI Server", [*venv_python_cmd(), "-m", "uvicorn", "app.main:app", "--app-dir", "dashboard/ai-server", "--host", "0.0.0.0", "--port", "8100"], ROOT_DIR))
        processes.append(start_process("Dashboard Backend", backend_bootrun_command(BACKEND_DIR), BACKEND_DIR))
        processes.append(start_process("Dashboard Frontend", ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4173"], FRONTEND_DIR))
        wait_for_dev_services(processes)
        while True:
            ensure_processes_running(processes)
            time.sleep(1)
    except KeyboardInterrupt:
        print(prefixed("dev 모드를 종료합니다."))
    finally:
        for _, process in reversed(processes):
            terminate_process(process)


def task_sample_dev() -> None:
    """
    `sample_dev` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_command_available()`, `ensure_sample_runtime_generated()`, `ensure_frontend_dependencies()`, `ensure_gradle_runtime()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.
    """
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    ensure_sample_runtime_generated()
    ensure_frontend_dependencies(SAMPLE_FRONTEND_DIR, label="sample-service frontend")
    ensure_gradle_runtime(SAMPLE_BACKEND_DIR)
    processes: list[tuple[str, subprocess.Popen[bytes]]] = []
    try:
        processes.append(start_process("Sample AI Server", [*venv_python_cmd(), "-m", "uvicorn", "app.main:app", "--app-dir", "projects/sample-service/ai-server", "--host", "0.0.0.0", "--port", "8000"], ROOT_DIR))
        processes.append(start_process("Sample Backend", backend_bootrun_command(SAMPLE_BACKEND_DIR), SAMPLE_BACKEND_DIR))
        processes.append(start_process("Sample Frontend", ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"], SAMPLE_FRONTEND_DIR))
        wait_for_sample_services(processes)
        while True:
            ensure_processes_running(processes)
            time.sleep(1)
    except KeyboardInterrupt:
        print(prefixed("sample-dev 모드를 종료합니다."))
    finally:
        for _, process in reversed(processes):
            terminate_process(process)


def task_validate_spec() -> None:
    """
    `validate_spec` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `run_specyn()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    run_specyn(["validate", "--spec-dir", "specs/001-sample-service"])


def task_init_spec() -> None:
    """
    `init_spec` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `run_specyn()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    run_specyn(["init-spec", "--project-id", "sample-service", "--output-dir", "specs/001-sample-service"])


def task_compile_prompts() -> None:
    """
    `compile_prompts` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `run_specyn()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    run_specyn(["compile-prompts", "--spec-dir", "specs/001-sample-service", "--output-dir", ".specyn/prompts/sample-service", "--workspace", ".workspace/sample-service"])


def task_run_sim() -> None:
    """
    `run_sim` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `run_specyn()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    run_specyn(["run", "--spec-dir", "specs/001-sample-service", "--workspace", ".workspace/sample-service", "--runtime", "simulate"])


def task_run_example() -> None:
    """
    `run_example` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `run_specyn()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    run_specyn(["run", "--spec-dir", "specs/001-sample-service", "--backend-url", "http://localhost:8180", "--workspace", ".workspace/sample-service"])


def task_sample_flow() -> None:
    """
    `sample_flow` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `task_validate_spec()`, `task_compile_prompts()`, `run_specyn()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    task_validate_spec()
    task_compile_prompts()
    run_specyn(["run", "--spec-dir", "specs/001-sample-service", "--project-id", "sample-service", "--workspace", ".workspace/sample-service"])


def task_test_python() -> None:
    """
    `test_python` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `run_checked()`, `venv_python_cmd()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    run_checked([*venv_python_cmd(), "-m", "pytest", "dashboard/ai-server/tests", "tools/tests", "scripts/tests", "-q"], cwd=ROOT_DIR)


def task_build_frontend() -> None:
    """
    `build_frontend` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `ensure_command_available()`, `run_checked()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    run_checked(["npm", "run", "build"], cwd=FRONTEND_DIR)


def task_ci_local() -> None:
    """
    `ci_local` 태스크의 실제 실행 로직을 수행한다.

    주요 흐름은 `run_checked()`, `venv_python_cmd()`, `resolve_gradle_command()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    run_checked([*venv_python_cmd(), "ci/check_spec_bundle.py"], cwd=ROOT_DIR)
    run_checked([*venv_python_cmd(), "-m", "pytest", "dashboard/ai-server/tests", "tools/tests", "scripts/tests", "-q"], cwd=ROOT_DIR)
    run_checked([*venv_python_cmd(), "-m", "ruff", "format", "--check", "dashboard/ai-server", "tools", "ci", "scripts", "specyn.py"], cwd=ROOT_DIR)
    run_checked(["npm", "run", "build"], cwd=FRONTEND_DIR)
    run_checked([*resolve_gradle_command(BACKEND_DIR), "test"], cwd=BACKEND_DIR)


TASKS = {
    "bootstrap": task_bootstrap,
    "doctor": task_doctor,
    "up": task_up,
    "dev": task_dev,
    "ai-server": task_ai_server,
    "backend": task_backend,
    "frontend": task_frontend,
    "sample-ai-server": task_sample_ai_server,
    "sample-backend": task_sample_backend,
    "sample-frontend": task_sample_frontend,
    "sample-dev": task_sample_dev,
    "validate-spec": task_validate_spec,
    "init-spec": task_init_spec,
    "compile-prompts": task_compile_prompts,
    "run-sim": task_run_sim,
    "run-example": task_run_example,
    "sample-flow": task_sample_flow,
    "test-python": task_test_python,
    "build-frontend": task_build_frontend,
    "ci-local": task_ci_local,
}


def build_parser() -> argparse.ArgumentParser:
    """
    스크립트 계층에서 CLI 인자 파서를 구성한다.

    주요 흐름은 `ArgumentParser()`, `add_argument()`, `keys()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        함수에서 조립한 `argparse.ArgumentParser` 타입 결과다.
    """
    parser = argparse.ArgumentParser(description="Specyn task runner")
    parser.add_argument("task", choices=TASKS.keys())
    return parser


def main() -> int:
    """
    스크립트 계층에서 메인 진입점 역할을 수행한다.

    주요 흐름은 `build_parser()`, `parse_args()`, `TASKS[args.task]()`, `exit_with()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    parser = build_parser()
    args = parser.parse_args()
    try:
        TASKS[args.task]()
    except TaskError as error:
        return exit_with(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
