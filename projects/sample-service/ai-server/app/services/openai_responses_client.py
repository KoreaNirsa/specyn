from __future__ import annotations

from typing import Any

try:
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    AsyncOpenAI = None  # type: ignore

from app.core.config import Settings


class OpenAIResponsesClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: Any | None = None
        if settings.openai_api_key and AsyncOpenAI is not None:
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )

    async def complete(self, prompt: str) -> str:
        if self.client is None:
            if self.settings.openai_api_key and AsyncOpenAI is None:
                return (
                    "[mock-mode] openai 패키지가 설치되지 않아 실제 모델 호출 대신 "
                    "프롬프트 기반 요약 모드로 동작합니다."
                )
            return (
                "[mock-mode] OPENAI_API_KEY가 없어 실제 모델 호출 대신 "
                "프롬프트 기반 요약 모드로 동작합니다."
            )

        response = await self.client.responses.create(
            model=self.settings.openai_model,
            input=prompt,
        )

        output_text = getattr(response, "output_text", None)
        if output_text:
            return str(output_text)

        return "[empty-response] Responses API에서 텍스트 출력이 비어 있습니다."
