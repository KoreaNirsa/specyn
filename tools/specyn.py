from __future__ import annotations

import argparse
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
VENV_REEXEC_ENV = "SPECYN_RUNNING_FROM_REPO_VENV"
LOCAL_GRADLE_VERSION = os.environ.get("SPECYN_GRADLE_VERSION", "8.14")
LOCAL_GRADLE_DIR = ROOT_DIR / ".specyn" / "tools" / f"gradle-{LOCAL_GRADLE_VERSION}"
WINDOWS_SHELL_EXTENSIONS = {".cmd", ".bat"}


def is_windows() -> bool:
    return os.name == "nt"


def format_command(command: list[str]) -> str:
    if is_windows():
        return subprocess.list2cmdline(command)
    return " ".join(shlex.quote(part) for part in command)


def repo_venv_python() -> Path | None:
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


def normalize_path(value: str) -> str:
    return str(Path(value))


def should_reexec_into_repo_venv(command: str | None) -> bool:
    if command in {None, "doctor"}:
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
    venv_python = repo_venv_python()
    if venv_python is None:
        return

    env = os.environ.copy()
    env[VENV_REEXEC_ENV] = "1"
    command = [str(venv_python), str(ROOT_DIR / "specyn.py"), *sys.argv[1:]]
    raise SystemExit(subprocess.call(command, cwd=str(ROOT_DIR), env=env))


def load_prompt_tooling() -> tuple[Any, Any, Any, Any, Any] | None:
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
    try:
        from tools.local_sdd_runtime import LocalSddRuntime
    except ModuleNotFoundError as error:
        print(f"TOOLING_IMPORT_FAILED: {error}")
        return None
    return LocalSddRuntime


def load_bundle_or_report(load_spec_bundle: Any, spec_dir: str) -> dict[str, Any] | None:
    try:
        return load_spec_bundle(Path(spec_dir))
    except (FileNotFoundError, ValueError) as error:
        print(f"SPEC_LOAD_FAILED: {error}")
        return None


def bundle_to_request(project_id: str, bundle: dict[str, Any], workspace: str, rag_enabled: bool) -> dict[str, Any]:
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
    prepared = prepare_command_for_subprocess(command)
    item: dict[str, Any] = {"available": True}
    if source is not None:
        item["source"] = source

    try:
        completed = subprocess.run(prepared, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False, text=True)
        first_line = (completed.stdout or "").splitlines()[0] if completed.stdout else ""
        item["version"] = first_line
    except Exception as error:  # pragma: no cover
        item["available"] = False
        item["version"] = f"ERR: {error}"
        item["command"] = format_command(prepared)

    return item


def resolve_project_id(project_id: str | None, spec_dir: str) -> str:
    return project_id.strip() if project_id and project_id.strip() else Path(spec_dir).name


def resolve_workspace_path(workspace: str | None, project_id: str) -> str:
    return normalize_path(workspace) if workspace and workspace.strip() else normalize_path(Path(".workspace") / project_id)


def resolve_project_output_root(project_id: str) -> Path:
    return ROOT_DIR / "projects" / project_id


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT_DIR))
    except ValueError:
        return str(path)


def print_validation_issues(issues: list[Any]) -> None:
    for issue in issues:
        print(f"[{issue.level}] {issue.code}: {issue.message}")


def cmd_validate(args: argparse.Namespace) -> int:
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
        prompt = compile_prompt(agent_name=step.agent, bundle=bundle, previous_outputs=previous_outputs, workspace_path=workspace_path)
        target = output_dir / f"{step.label}.prompt.md"
        target.write_text(prompt, encoding="utf-8")
        previous_outputs.append(f"{step.label}: prompt compiled -> {target}")
        print(f"PROMPT_WRITTEN {target}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
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
    request_body = bundle_to_request(project_id=project_id, bundle=bundle, workspace=workspace_path, rag_enabled=args.rag_enabled)

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
    local_result = runtime.execute(project_id=project_id, bundle=bundle, workspace_path=workspace_path, rag_enabled=args.rag_enabled, runtime_mode=args.runtime)
    print(json.dumps({
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
    }, ensure_ascii=False, indent=2))
    return 0 if local_result.status in {"COMPLETED", "SIMULATED"} else 1


def cmd_doctor(_: argparse.Namespace) -> int:
    report: dict[str, dict[str, Any]] = {"python": command_report([sys.executable, "--version"], source="current-interpreter")}
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

    report["venv"] = {"available": repo_venv_python() is not None, "python": str(repo_venv_python()) if repo_venv_python() is not None else None}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
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
    run_parser.add_argument("--runtime", choices=("local", "simulate"), default="local", help="backend-url 없이 실행할 때 사용할 로컬 런타임 모드")
    run_parser.set_defaults(func=cmd_run)

    doctor_parser = subparsers.add_parser("doctor", help="로컬 실행 환경 점검")
    doctor_parser.set_defaults(func=cmd_doctor)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if should_reexec_into_repo_venv(args.command):
        reexec_into_repo_venv()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
