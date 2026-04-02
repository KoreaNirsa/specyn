"""
OpenAI Responses API 호출을 캡슐화하면서 SDK 부재나 인증 모드에 따른 mock 경로까지 함께 제공하는 클라이언트 모듈이다.
실제 API 호출과 테스트/로컬 개발용 요약 대체 경로를 한 클래스 안에 두어 상위 서비스가 복잡한 분기 처리를 직접 알 필요가 없게 한다.
"""

from __future__ import annotations

import inspect
from typing import Any

try:
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    AsyncOpenAI = None  # type: ignore

from app.core.config import Settings


class OpenAIResponsesClient:
    """
    AI Server 서비스 계층에서 사용되는 `OpenAIResponsesClient` 클래스다.

    외부에서 주로 읽어야 할 메서드는 `complete()`이다.

    Attributes:
        settings: 런타임 동작을 제어하는 설정 객체다.
        client: 인스턴스가 내부적으로 유지하는 client 관련 상태다.
    """

    def __init__(self, settings: Settings):
        """
        `OpenAIResponsesClient` 인스턴스가 사용할 기본 상태와 협력 객체를 준비한다.

        주요 흐름은 `AsyncOpenAI()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

        Args:
            settings: 런타임 동작을 제어하는 설정 객체다.
        """
        self.settings = settings
        self.client: Any | None = None
        if (
            settings.specyn_auth_mode == "openapi"
            and settings.openai_api_key
            and AsyncOpenAI is not None
        ):
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )

    async def complete(self, prompt: str, event_sink: Any | None = None) -> str:
        """
        `OpenAIResponsesClient`의 공개 메서드로, `complete()`가 맡는 작업 관련 작업을 수행한다.

        주요 흐름은 `_emit()`, `create()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.

        Args:
            prompt: LLM 또는 Codex에 전달할 프롬프트 전문이다.
            event_sink: 진행 로그를 실시간으로 전달할 콜백 또는 비동기 콜백이다.

        Returns:
            후속 처리나 출력에 사용할 문자열 결과다.
        """
        await self._emit(event_sink, f"Responses request prepared (mode={self.settings.specyn_auth_mode}).")

        if self.client is None:
            if (
                self.settings.specyn_auth_mode == "openapi"
                and self.settings.openai_api_key
                and AsyncOpenAI is None
            ):
                await self._emit(event_sink, "OpenAI SDK is unavailable, switching to mock-mode summary.")
                return (
                    "[mock-mode] openai package is unavailable, so a prompt-based summary is returned instead of a live model call."
                )
            if self.settings.specyn_auth_mode != "openapi":
                await self._emit(
                    event_sink,
                    "ChatGPT auth mode detected, returning mock summary before optional Codex execution.",
                )
                return (
                    "[mock-mode] SPECYN_AUTH_MODE=chatgpt so a prompt-based summary is returned before Codex execution."
                )
            await self._emit(event_sink, "OPENAI_API_KEY is missing, returning mock summary.")
            return (
                "[mock-mode] OPENAI_API_KEY is missing, so a prompt-based summary is returned instead of a live model call."
            )

        await self._emit(event_sink, f"Calling Responses API with model={self.settings.openai_model}.")
        response = await self.client.responses.create(
            model=self.settings.openai_model,
            input=prompt,
        )

        output_text = getattr(response, "output_text", None)
        if output_text:
            await self._emit(event_sink, "Responses API returned a text summary.")
            return str(output_text)

        await self._emit(event_sink, "Responses API returned no text output.")
        return "[empty-response] Responses API returned no text output."

    async def _emit(self, event_sink: Any | None, message: str) -> None:
        """
        `OpenAIResponsesClient` 내부에서만 사용하는 보조 메서드로, `emit()`가 맡는 작업 관련 작업을 수행한다.

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
