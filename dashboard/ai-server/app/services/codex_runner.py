"""
AI Server 내부에서 Codex CLI를 비동기로 실행하고, 모델 fallback과 스트리밍 로그를 처리하는 실행기 모듈이다.
프롬프트 스냅샷 저장, 워크스페이스 준비, 표준 출력/오류 스트림 중계, 타임아웃/용량 부족 대응까지 Codex 호출의 운영상 세부사항을 캡슐화한다.
"""

import asyncio
import inspect
import os
from pathlib import Path
import shlex
from typing import Any

from app.core.config import Settings


class CodexRunner:
    """
    외부 도구나 실행 경로를 감싸 실제 수행을 책임지는 러너 클래스다.

    외부에서 주로 읽어야 할 메서드는 `run()`이다.

    Attributes:
        settings: 런타임 동작을 제어하는 설정 객체다.
    """

    def __init__(self, settings: Settings):
        """
        `CodexRunner` 인스턴스가 사용할 기본 상태와 협력 객체를 준비한다.

        외부 협력 객체 호출보다 현재 스코프의 값 비교와 간단한 계산에 집중한 헬퍼다.

        Args:
            settings: 런타임 동작을 제어하는 설정 객체다.
        """
        self.settings = settings

    async def run(
        self,
        prompt: str,
        workspace: str | None,
        event_sink: Any | None = None,
    ) -> tuple[str, list[str]]:
        """
        `CodexRunner`의 공개 메서드로, 작업을(를) 실제로 실행한다.

        주요 흐름은 `_emit()`, `format()`, `create_subprocess_exec()`, `_build_subprocess_env()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Args:
            prompt: LLM 또는 Codex에 전달할 프롬프트 전문이다.
            workspace: 작업 또는 생성 대상 워크스페이스 경로다.
            event_sink: 진행 로그를 실시간으로 전달할 콜백 또는 비동기 콜백이다.

        Returns:
            함수에서 조립한 `tuple[str, list[str]]` 타입 결과다.
        """
        if self.settings.codex_exec_mode == "disabled":
            await self._emit(event_sink, "Codex execution is disabled by CODEX_EXEC_MODE=disabled.")
            return (
                "[codex-disabled] CODEX_EXEC_MODE=disabled so only the execution plan is returned.",
                [],
            )

        if self.settings.codex_exec_mode != "cli":
            await self._emit(event_sink, f"Unsupported CODEX_EXEC_MODE={self.settings.codex_exec_mode}.")
            return (
                "[codex-unsupported] only cli mode is currently supported.",
                [],
            )

        if not workspace:
            await self._emit(event_sink, "workspacePath is missing, skipping Codex CLI execution.")
            return ("[codex-skip] workspacePath is missing, so Codex CLI was not executed.", [])

        workspace_path = Path(workspace).resolve()
        workspace_path.mkdir(parents=True, exist_ok=True)
        snapshot_dir = workspace_path / ".specyn"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        (snapshot_dir / "last_codex_prompt.md").write_text(prompt, encoding="utf-8")

        last_error = ""
        attempted_models: list[str] = []

        for model in self.settings.codex_model_candidates:
            attempted_models.append(model)
            command = self.settings.codex_command_template.format(
                workspace=str(workspace_path),
                model=model,
            )
            await self._emit(event_sink, f"Starting Codex CLI with model={model}.")

            process = await asyncio.create_subprocess_exec(
                *shlex.split(command),
                cwd=str(workspace_path),
                env=self._build_subprocess_env(workspace_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout_lines: list[str] = []
            stderr_lines: list[str] = []
            stdout_task = asyncio.create_task(self._drain_stream(process.stdout, stdout_lines, event_sink, "stdout"))
            stderr_task = asyncio.create_task(self._drain_stream(process.stderr, stderr_lines, event_sink, "stderr"))

            try:
                if process.stdin is not None:
                    process.stdin.write(prompt.encode("utf-8"))
                    await process.stdin.drain()
                    process.stdin.close()
                await asyncio.wait_for(process.wait(), timeout=self.settings.codex_timeout_seconds)
                await stdout_task
                await stderr_task
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                stdout_task.cancel()
                stderr_task.cancel()
                await self._emit(event_sink, f"Codex CLI timed out after {self.settings.codex_timeout_seconds} seconds.")
                return (
                    f"[codex-error] model={model} command timed out after {self.settings.codex_timeout_seconds} seconds",
                    [],
                )

            text = "\n".join(stdout_lines).strip()
            err = "\n".join(stderr_lines).strip()
            message = err or text

            if process.returncode == 0:
                generated_files = [
                    line.removeprefix("FILE:").strip()
                    for line in text.splitlines()
                    if line.startswith("FILE:")
                ]
                await self._emit(event_sink, f"Codex CLI finished successfully with model={model}.")
                if model != self.settings.codex_model:
                    text = f"[codex-fallback] model={model}\n{text}".strip()
                return (text or "[codex-ok] execution complete", generated_files)

            last_error = f"[codex-error] model={model} {message}".strip()
            await self._emit(event_sink, last_error)
            if not self._is_capacity_error(message):
                return (last_error, [])

            await self._emit(event_sink, f"Model {model} is at capacity, trying the next fallback model.")

        attempted = ", ".join(attempted_models)
        await self._emit(event_sink, f"All fallback models failed. attempted={attempted}")
        return (
            f"{last_error}\n[codex-fallback-failed] attempted models: {attempted}",
            [],
        )

    async def _drain_stream(
        self,
        stream: asyncio.StreamReader | None,
        collected: list[str],
        event_sink: Any | None,
        channel: str,
    ) -> None:
        """
        `CodexRunner` 내부에서만 사용하는 보조 메서드로, `drain_stream()`가 맡는 스트림 관련 작업을 수행한다.

        주요 흐름은 `readline()`, `_emit()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Args:
            stream: 비동기 표준 출력/오류 스트림이다.
            collected: 스트림에서 읽은 로그 라인을 누적할 리스트다.
            event_sink: 진행 로그를 실시간으로 전달할 콜백 또는 비동기 콜백이다.
            channel: 로그가 들어온 스트림 채널 이름이다.
        """
        if stream is None:
            return

        while True:
            line = await stream.readline()
            if not line:
                break
            message = line.decode("utf-8", errors="replace").rstrip()
            if not message:
                continue
            collected.append(message)
            prefix = "[stderr]" if channel == "stderr" else "[stdout]"
            await self._emit(event_sink, f"{prefix} {message}")

    async def _emit(self, event_sink: Any | None, message: str) -> None:
        """
        `CodexRunner` 내부에서만 사용하는 보조 메서드로, `emit()`가 맡는 작업 관련 작업을 수행한다.

        주요 흐름은 `event_sink()`, `isawaitable()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

        Args:
            event_sink: 진행 로그를 실시간으로 전달할 콜백 또는 비동기 콜백이다.
            message: 출력하거나 전달할 메시지 문자열이다.
        """
        if event_sink is None:
            return
        result = event_sink(message)
        if inspect.isawaitable(result):
            await result

    def _build_subprocess_env(self, workspace_path: Path) -> dict[str, str]:
        """
        `CodexRunner` 내부에서만 사용하는 보조 메서드로, 하위 프로세스 환경 변수을(를) 조립하거나 생성한다.

        주요 흐름은 `pop()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

        Args:
            workspace_path: 문자열 또는 Path 형태로 전달된 워크스페이스 경로다.

        Returns:
            키 기반으로 정리한 매핑 결과다.
        """
        env = os.environ.copy()
        env["CODEX_HOME"] = str((self.settings.project_root / self.settings.codex_home).resolve())

        # Codex CLI should not inherit deprecated or conflicting OpenAI env vars in ChatGPT mode.
        env.pop("OPENAI_BASE_URL", None)
        env.pop("OPENAI_MODEL", None)

        if self.settings.specyn_auth_mode == "chatgpt":
            env.pop("OPENAI_API_KEY", None)

        return env

    def _is_capacity_error(self, message: str) -> bool:
        """
        `CodexRunner` 내부에서만 사용하는 보조 메서드로, capacity 오류 여부를 판단한다.

        주요 흐름은 `lower()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

        Args:
            message: 출력하거나 전달할 메시지 문자열이다.

        Returns:
            조건 충족 여부를 나타내는 불리언 값이다.
        """
        normalized = message.lower()
        return "at capacity" in normalized or "try a different model" in normalized
