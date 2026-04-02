"""
`codex runner`가 표준 런타임 scaffold를 먼저 보장하는지 확인한다.
"""

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "dashboard" / "ai-server"))

from app.core.config import Settings  # noqa: E402
from app.services.codex_runner import CodexRunner  # noqa: E402


class _FakeStdin:
    def __init__(self) -> None:
        self.buffer = bytearray()
        self.closed = False

    def write(self, data: bytes) -> None:
        self.buffer.extend(data)

    async def drain(self) -> None:
        return None

    def close(self) -> None:
        self.closed = True


class _FakeStream:
    def __init__(self, lines: list[str] | None = None) -> None:
        self._lines = [line.encode("utf-8") for line in (lines or [])]

    async def readline(self) -> bytes:
        if self._lines:
            return self._lines.pop(0)
        return b""


class _FakeProcess:
    def __init__(self) -> None:
        self.stdin = _FakeStdin()
        self.stdout = _FakeStream()
        self.stderr = _FakeStream()
        self.returncode = 0

    async def wait(self) -> int:
        return self.returncode

    def kill(self) -> None:
        self.returncode = -9


@pytest.mark.asyncio
async def test_codex_runner_prepares_standard_runtime_scaffold(monkeypatch, tmp_path: pathlib.Path) -> None:
    """
    Codex 실행 전에 sample-up 계약 파일이 workspace에 존재해야 한다.
    """
    settings = Settings(
        codex_exec_mode="cli",
        codex_command_template="codex exec --model {model} -C {workspace}",
    )
    runner = CodexRunner(settings)
    workspace = tmp_path / "projects" / "sample-service"

    async def fake_create_subprocess_exec(*args, **kwargs):
        return _FakeProcess()

    monkeypatch.setattr("asyncio.create_subprocess_exec", fake_create_subprocess_exec)

    result, generated_files = await runner.run("test prompt", str(workspace))

    assert result == "[codex-ok] execution complete"
    assert generated_files == []
    assert (workspace / "docker-compose.local.yml").exists()
    assert "name: sample-service" in (workspace / "docker-compose.local.yml").read_text(encoding="utf-8")
    assert (workspace / ".specyn" / "last_codex_prompt.md").read_text(encoding="utf-8") == "test prompt"
