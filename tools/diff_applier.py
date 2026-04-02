"""
생성된 patch를 워크스페이스에 저장하고 `git apply`로 반영할 때 사용하는 최소 단위 유틸리티 모듈이다.
로컬 런타임이나 후처리 단계에서 diff 텍스트를 다룰 때 파일 저장과 실제 적용을 분리해 재사용할 수 있게 한다.
"""

from __future__ import annotations

from pathlib import Path
import subprocess


def save_patch(workspace: Path, patch_text: str, filename: str = "generated.patch") -> Path:
    """
    도구 계층에서 패치을(를) 저장한다.

    주요 흐름은 `mkdir()`, `write_text()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        workspace: 작업 또는 생성 대상 워크스페이스 경로다.
        patch_text: 저장하거나 적용할 unified diff 텍스트다.
        filename: 저장할 파일 이름이다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    workspace.mkdir(parents=True, exist_ok=True)
    patch_path = workspace / filename
    patch_path.write_text(patch_text, encoding="utf-8")
    return patch_path


def apply_patch(workspace: Path, patch_path: Path) -> subprocess.CompletedProcess[bytes]:
    """
    도구 계층에서 패치을(를) 적용한다.

    주요 흐름은 `run()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        workspace: 작업 또는 생성 대상 워크스페이스 경로다.
        patch_path: 적용할 patch 파일 경로다.

    Returns:
        외부 명령 실행 결과를 담은 `subprocess.CompletedProcess` 객체다.
    """
    return subprocess.run(
        ["git", "apply", str(patch_path)],
        cwd=workspace,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
