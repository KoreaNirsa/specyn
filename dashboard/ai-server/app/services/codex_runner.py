import asyncio
from pathlib import Path
import shlex

from app.core.config import Settings


class CodexRunner:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def run(self, prompt: str, workspace: str | None) -> tuple[str, list[str]]:
        if self.settings.codex_exec_mode == "disabled":
            return (
                "[codex-disabled] CODEX_EXEC_MODE=disabled 이므로 실제 코드 생성 대신 실행 계획만 반환합니다.",
                [],
            )

        if self.settings.codex_exec_mode != "cli":
            return (
                "[codex-unsupported] 현재 예제 스캐폴드는 cli 모드만 구현합니다.",
                [],
            )

        if not workspace:
            return ("[codex-skip] workspacePath가 없어 Codex CLI를 실행하지 않았습니다.", [])

        workspace_path = Path(workspace)
        workspace_path.mkdir(parents=True, exist_ok=True)
        snapshot_dir = workspace_path / ".specyn"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        (snapshot_dir / "last_codex_prompt.md").write_text(prompt, encoding="utf-8")

        command = self.settings.codex_command_template.format(workspace=str(workspace_path))
        process = await asyncio.create_subprocess_exec(
            *shlex.split(command),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=prompt.encode("utf-8")),
            timeout=self.settings.codex_timeout_seconds,
        )
        text = stdout.decode("utf-8").strip()
        err = stderr.decode("utf-8").strip()

        if process.returncode != 0:
            return (f"[codex-error] {err or text}", [])

        generated_files = [
            line.removeprefix("FILE:").strip()
            for line in text.splitlines()
            if line.startswith("FILE:")
        ]
        return (text or "[codex-ok] 실행 완료", generated_files)
