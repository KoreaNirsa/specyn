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
    pass


def prefixed(message: str) -> str:
    return f"[specyn] {message}"


def exit_with(message: str, code: int = 1) -> int:
    print(prefixed(message), file=sys.stderr)
    return code


def is_windows() -> bool:
    return os.name == "nt"


def format_command(command: list[str]) -> str:
    if is_windows():
        return subprocess.list2cmdline(command)
    return " ".join(shlex.quote(part) for part in command)


def clean_env() -> dict[str, str]:
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
    if url.startswith(NPM_PUBLIC_REGISTRY):
        return url
    if NPM_PUBLIC_MIRROR_MARKER in url:
        _, _, package_path = url.partition(NPM_PUBLIC_MIRROR_MARKER)
        return f"{NPM_PUBLIC_REGISTRY}{package_path.lstrip('/')}"
    return url


def sanitize_npm_lockfile(lockfile_path: Path | None = None) -> int:
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
    if not VENV_PYTHON.exists():
        raise TaskError(".venv가 없습니다. 먼저 `make bootstrap` 또는 `python scripts/specyn_tasks.py bootstrap`을 실행하세요.")
    return [str(VENV_PYTHON)]


def local_gradle_executable() -> Path:
    executable = "gradle.bat" if is_windows() else "gradle"
    return LOCAL_GRADLE_DIR / "bin" / executable


def prepare_command_for_subprocess(command: list[str]) -> list[str]:
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
    env = clean_env()
    if extra_env:
        env.update(extra_env)
    working_dir = cwd or ROOT_DIR
    prepared_command = prepare_command_for_subprocess(command)
    completed = subprocess.run(prepared_command, cwd=working_dir, env=env)
    if completed.returncode != 0:
        raise TaskError(f"명령 실행 실패: {format_command(prepared_command)} (exit={completed.returncode})")


def ensure_command_available(binary: str, *, purpose: str) -> None:
    if shutil.which(binary) is None:
        raise TaskError(f"`{binary}` 명령을 찾을 수 없습니다. {purpose}")


def ensure_env_file() -> None:
    env_example = ROOT_DIR / ".env.example"
    env_file = ROOT_DIR / ".env"
    if not env_file.exists():
        shutil.copy2(env_example, env_file)
        print(prefixed(".env.example -> .env 복사 완료"))


def ensure_runtime_dirs() -> None:
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


def gradle_distribution_url() -> str:
    return f"https://services.gradle.org/distributions/gradle-{LOCAL_GRADLE_VERSION}-bin.zip"


def ensure_local_gradle() -> Path:
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
    return [*resolve_gradle_command(backend_dir), "--console=plain", "--no-daemon", "--quiet", "bootRun"]


def service_responding(url: str, *, timeout: float = 2.0) -> bool:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return 200 <= getattr(response, "status", 200) < 500
    except urllib.error.HTTPError as exc:
        return 200 <= exc.code < 500
    except Exception:
        return False


def ensure_processes_running(processes: list[tuple[str, subprocess.Popen[bytes]]]) -> None:
    for name, process in processes:
        return_code = process.poll()
        if return_code is None:
            continue
        if return_code == 0:
            raise TaskError(f"{name} 프로세스가 종료되어 dev 모드를 중단합니다.")
        raise TaskError(f"{name} 프로세스가 비정상 종료되었습니다. exit={return_code}")


def wait_for_dev_services(processes: list[tuple[str, subprocess.Popen[bytes]]]) -> None:
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
    run_checked([*venv_python_cmd(), str(SPECYN_ENTRYPOINT), *command], cwd=ROOT_DIR)


def task_bootstrap() -> None:
    ensure_env_file()
    ensure_runtime_dirs()
    if not VENV_PYTHON.exists():
        run_checked([*system_python_cmd(), "-m", "venv", str(VENV_DIR)], cwd=ROOT_DIR)
    run_checked([*venv_python_cmd(), "-m", "pip", "install", "--upgrade", "pip"], cwd=ROOT_DIR)
    run_checked([*venv_python_cmd(), "-m", "pip", "install", "-r", "dashboard/ai-server/requirements.txt", "-r", "dashboard/ai-server/requirements-dev.txt", "-r", "tools/requirements.txt"], cwd=ROOT_DIR)
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    sanitize_npm_lockfile(FRONTEND_DIR / "package-lock.json")
    run_checked(frontend_npm_install_command(FRONTEND_DIR), cwd=FRONTEND_DIR)
    if (SAMPLE_FRONTEND_DIR / "package-lock.json").exists():
        sanitize_npm_lockfile(SAMPLE_FRONTEND_DIR / "package-lock.json")
    run_checked(frontend_npm_install_command(SAMPLE_FRONTEND_DIR), cwd=SAMPLE_FRONTEND_DIR)
    maybe_bootstrap_gradle()
    print(prefixed("bootstrap 완료"))


def task_doctor() -> None:
    python_command = [*venv_python_cmd(), str(SPECYN_ENTRYPOINT), "doctor"] if VENV_PYTHON.exists() else [*system_python_cmd(), str(SPECYN_ENTRYPOINT), "doctor"]
    run_checked(python_command, cwd=ROOT_DIR)


def task_up() -> None:
    ensure_command_available("docker", purpose="Docker Desktop 또는 Docker Engine + Compose v2를 설치하세요.")
    run_checked(["docker", "compose", "-f", "docker-compose.local.yml", "up", "--build"], cwd=ROOT_DIR)


def task_ai_server() -> None:
    run_checked([*venv_python_cmd(), "-m", "uvicorn", "app.main:app", "--app-dir", "dashboard/ai-server", "--host", "0.0.0.0", "--port", "8100", "--reload"], cwd=ROOT_DIR)


def task_backend() -> None:
    run_checked(backend_bootrun_command(BACKEND_DIR), cwd=BACKEND_DIR)


def task_frontend() -> None:
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    run_checked(["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "4173"], cwd=FRONTEND_DIR)


def task_sample_ai_server() -> None:
    run_checked([*venv_python_cmd(), "-m", "uvicorn", "app.main:app", "--app-dir", "projects/sample-service/ai-server", "--host", "0.0.0.0", "--port", "8000", "--reload"], cwd=ROOT_DIR)


def task_sample_backend() -> None:
    run_checked(backend_bootrun_command(SAMPLE_BACKEND_DIR), cwd=SAMPLE_BACKEND_DIR)


def task_sample_frontend() -> None:
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    run_checked(["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"], cwd=SAMPLE_FRONTEND_DIR)


def terminate_process(process: subprocess.Popen[bytes]) -> None:
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
    prepared_command = prepare_command_for_subprocess(command)
    creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if is_windows() else 0
    process = subprocess.Popen(prepared_command, cwd=cwd, creationflags=creationflags)
    print(prefixed(f"{name} 시작: {format_command(prepared_command)}"))
    return name, process


def task_dev() -> None:
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    processes: list[tuple[str, subprocess.Popen[bytes]]] = []
    try:
        processes.append(start_process("Dashboard AI Server", [*venv_python_cmd(), "-m", "uvicorn", "app.main:app", "--app-dir", "dashboard/ai-server", "--host", "0.0.0.0", "--port", "8100", "--reload"], ROOT_DIR))
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
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    processes: list[tuple[str, subprocess.Popen[bytes]]] = []
    try:
        processes.append(start_process("Sample AI Server", [*venv_python_cmd(), "-m", "uvicorn", "app.main:app", "--app-dir", "projects/sample-service/ai-server", "--host", "0.0.0.0", "--port", "8000", "--reload"], ROOT_DIR))
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
    run_specyn(["validate", "--spec-dir", "specs/projects/sample-service"])


def task_init_spec() -> None:
    run_specyn(["init-spec", "--project-id", "sample-service", "--output-dir", "specs/projects/sample-service"])


def task_compile_prompts() -> None:
    run_specyn(["compile-prompts", "--spec-dir", "specs/projects/sample-service", "--output-dir", ".specyn/prompts/sample-service", "--workspace", ".workspace/sample-service"])


def task_run_sim() -> None:
    run_specyn(["run", "--spec-dir", "specs/projects/sample-service", "--workspace", ".workspace/sample-service", "--runtime", "simulate"])


def task_run_example() -> None:
    run_specyn(["run", "--spec-dir", "specs/projects/sample-service", "--backend-url", "http://localhost:8180", "--workspace", ".workspace/sample-service"])


def task_sample_flow() -> None:
    task_validate_spec()
    task_compile_prompts()
    run_specyn(["run", "--spec-dir", "specs/projects/sample-service", "--project-id", "sample-service", "--workspace", ".workspace/sample-service"])


def task_test_python() -> None:
    run_checked([*venv_python_cmd(), "-m", "pytest", "dashboard/ai-server/tests", "tools/tests", "scripts/tests", "-q"], cwd=ROOT_DIR)


def task_build_frontend() -> None:
    ensure_command_available("npm", purpose="Node.js 20+와 npm을 설치한 뒤 다시 시도하세요.")
    run_checked(["npm", "run", "build"], cwd=FRONTEND_DIR)


def task_ci_local() -> None:
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
    parser = argparse.ArgumentParser(description="Specyn task runner")
    parser.add_argument("task", choices=TASKS.keys())
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        TASKS[args.task]()
    except TaskError as error:
        return exit_with(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
