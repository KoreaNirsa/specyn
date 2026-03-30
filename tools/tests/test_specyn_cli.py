from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from tools import specyn


ROOT = Path(__file__).resolve().parents[2]
ENTRYPOINT = ROOT / "specyn.py"


def _blocked_yaml_command(*args: str) -> list[str]:
    python_code = f"""
import builtins
import runpy
import sys

_real_import = builtins.__import__


def _guard(name, globals=None, locals=None, fromlist=(), level=0):
    if name == 'yaml' or name.startswith('yaml.'):
        raise ModuleNotFoundError("No module named 'yaml'")
    return _real_import(name, globals, locals, fromlist, level)


builtins.__import__ = _guard
sys.argv = [{repr(str(ENTRYPOINT))}, {", ".join(repr(arg) for arg in args)}]
runpy.run_path({repr(str(ENTRYPOINT))}, run_name='__main__')
"""
    return [sys.executable, "-c", python_code]


def test_reexec_into_repo_venv_uses_root_entrypoint(monkeypatch, tmp_path: Path) -> None:
    venv_python = tmp_path / ".venv" / "Scripts" / "python.exe"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_call(command, cwd, env):
        captured["command"] = command
        captured["cwd"] = cwd
        captured["env"] = env
        return 0

    monkeypatch.setattr(specyn, "repo_venv_python", lambda: venv_python)
    monkeypatch.setattr(specyn.subprocess, "call", fake_call)
    monkeypatch.setattr(specyn.sys, "argv", ["specyn.py", "init-spec", "--project-id", "demo"])

    try:
        specyn.reexec_into_repo_venv()
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("SystemExit was not raised")

    assert captured["command"] == [
        str(venv_python),
        str(specyn.ROOT_DIR / "specyn.py"),
        "init-spec",
        "--project-id",
        "demo",
    ]
    assert captured["cwd"] == str(specyn.ROOT_DIR)
    assert captured["env"][specyn.VENV_REEXEC_ENV] == "1"


def test_init_spec_runs_without_yaml_installed(tmp_path: Path) -> None:
    output_dir = tmp_path / "generated-specs"

    completed = subprocess.run(
        _blocked_yaml_command(
            "init-spec",
            "--project-id",
            "sample-service",
            "--output-dir",
            str(output_dir),
        ),
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert (output_dir / "product.md").exists()
    assert "CREATED" in completed.stdout
    assert completed.stderr == ""


def test_validate_reports_missing_yaml_dependency_cleanly(tmp_path: Path) -> None:
    completed = subprocess.run(
        _blocked_yaml_command(
            "validate",
            "--spec-dir",
            "specs/examples/todo-service",
        ),
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "TOOLING_IMPORT_FAILED" in completed.stdout
    assert "yaml" in completed.stdout
    assert "Traceback" not in completed.stderr
