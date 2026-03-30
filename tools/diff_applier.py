from __future__ import annotations

from pathlib import Path
import subprocess


def save_patch(workspace: Path, patch_text: str, filename: str = "generated.patch") -> Path:
    workspace.mkdir(parents=True, exist_ok=True)
    patch_path = workspace / filename
    patch_path.write_text(patch_text, encoding="utf-8")
    return patch_path


def apply_patch(workspace: Path, patch_path: Path) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "apply", str(patch_path)],
        cwd=workspace,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
