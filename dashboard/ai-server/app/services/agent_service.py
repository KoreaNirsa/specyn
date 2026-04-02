"""
agent 실행 요청을 프롬프트 생성, 요약 생성, 선택적 Codex 실행으로 분기해 처리하는 서비스 계층 모듈이다.
동일한 요청이라도 auth 모드와 agent 유형에 따라 LLM 요약만 수행할지, RAG 검색만 수행할지, Codex까지 이어서 실행할지를 이 서비스가 조정한다.
"""

import json
import asyncio
from collections.abc import AsyncIterator
from typing import Any

from app.core.config import get_settings
from app.models.contracts import AgentExecutionRequest, AgentExecutionResponse
from app.services.codex_runner import CodexRunner
from app.services.openai_responses_client import OpenAIResponsesClient
from app.services.prompt_builder import PromptBuilder
from app.services.rag_service import RagService

CODE_GENERATING_AGENTS = {"API", "BACKEND", "FRONTEND", "DBA", "DEVOPS", "TEST", "DOCS"}


def normalize_agent_name(agent_name: str) -> str:
    """
    AI Server 서비스 계층에서 agent name을(를) 일관된 표준 형태로 정규화한다.

    주요 흐름은 `lower()`, `replace()`, `strip()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        agent_name: 정규화 또는 조회할 agent 이름이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return agent_name.strip().lower().replace("_", "-")


def agent_key(agent_name: str) -> str:
    """
    AI Server 서비스 계층에서 `agent_key()`가 맡는 key 관련 작업을 수행한다.

    주요 흐름은 `normalize_agent_name()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        agent_name: 정규화 또는 조회할 agent 이름이다.

    Returns:
        후속 처리나 출력에 사용할 문자열 결과다.
    """
    return normalize_agent_name(agent_name).replace("-", "_").upper()


class AgentService:
    """
    AI Server 서비스 계층에서 핵심 비즈니스 흐름을 조율하는 서비스 클래스다.

    외부에서 주로 읽어야 할 메서드는 `execute()`, `execute_stream()`이다.

    Attributes:
        settings: 런타임 동작을 제어하는 설정 객체다.
        prompt_builder: 인스턴스가 내부적으로 유지하는 프롬프트 builder 관련 상태다.
        llm_client: 인스턴스가 내부적으로 유지하는 llm client 관련 상태다.
        codex_runner: 인스턴스가 내부적으로 유지하는 Codex runner 관련 상태다.
        rag_service: 인스턴스가 내부적으로 유지하는 RAG 서비스 관련 상태다.
    """

    def __init__(self) -> None:
        """
        `AgentService` 인스턴스가 사용할 기본 상태와 협력 객체를 준비한다.

        주요 흐름은 `get_settings()`, `PromptBuilder()`, `OpenAIResponsesClient()`, `CodexRunner()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        """
        settings = get_settings()
        self.settings = settings
        self.prompt_builder = PromptBuilder()
        self.llm_client = OpenAIResponsesClient(settings)
        self.codex_runner = CodexRunner(settings)
        self.rag_service = RagService()

    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResponse:
        """
        `AgentService`의 공개 메서드로, 작업 실행 흐름을 수행한다.

        주요 흐름은 `execute_stream()`, `AgentExecutionResponse()`, `RuntimeError()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Args:
            request: HTTP 요청 본문 또는 agent 실행 요청 모델이다.

        Returns:
            함수에서 조립한 `AgentExecutionResponse` 타입 결과다.

        Raises:
            RuntimeError: 선행 조건 위반이나 실행 실패처럼 즉시 중단이 필요한 상황에서 발생할 수 있다.
        """
        response: AgentExecutionResponse | None = None

        async for event in self.execute_stream(request):
            if event["type"] == "complete":
                response = AgentExecutionResponse(**event["response"])

        if response is None:
            raise RuntimeError("Agent execution finished without a completion payload.")
        return response

    async def execute_stream(self, request: AgentExecutionRequest) -> AsyncIterator[dict[str, Any]]:
        """
        `AgentService`의 공개 메서드로, 스트림 실행 흐름을 수행한다.

        주요 흐름은 `build()`, `normalize_agent_name()`, `agent_key()`, `search()`를 이용해 이벤트를 만들고, 이를 순차적으로 스트리밍하는 것이다.
        여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Args:
            request: HTTP 요청 본문 또는 agent 실행 요청 모델이다.

        Yields:
            호출 순서에 따라 외부 소비자가 이어서 처리할 이벤트 또는 스트림 항목이다.
        """
        prompt = self.prompt_builder.build(request)
        normalized_agent = normalize_agent_name(request.agent)
        agent_type = agent_key(request.agent)
        executor = "codex" if self.settings.specyn_auth_mode == "chatgpt" else "openai"

        validations = [
            "spec bundle validation complete",
            f"agent={normalized_agent} prompt assembled",
            f"previousResults={len(request.previousResults)}",
            f"authMode={self.settings.specyn_auth_mode}",
            f"executor={executor}",
        ]

        generated_files: list[str] = []
        raw_output = ""

        yield {"type": "status", "message": f"Prompt assembled for agent={normalized_agent}."}
        yield {"type": "status", "message": f"Executor selected: {executor}."}

        if agent_type == "RAG":
            query = f"{request.projectId} architecture spec review testing quality security performance"
            yield {"type": "log", "message": f"Running RAG search with query={query}."}
            rag_response = await self.rag_service.search(query, 5)
            summary_lines = [
                "[rag-results] Use the following context in later steps.",
                *[
                    f"- {item['source']} (score={item['score']}): {item['content'][:140]}"
                    for item in rag_response.items
                ],
            ]
            summary = "\n".join(summary_lines)
            raw_output = json.dumps(rag_response.model_dump(), ensure_ascii=False, indent=2)
            validations.append("RAG search complete")
            yield {"type": "status", "message": "RAG search completed."}
            yield {
                "type": "complete",
                "response": AgentExecutionResponse(
                    status="COMPLETED",
                    summary=summary,
                    executor="rag",
                    generatedFiles=generated_files,
                    validations=validations,
                    promptPreview=prompt[:2000],
                    rawOutput=raw_output,
                ).model_dump(),
            }
            return

        yield {"type": "status", "message": "Starting summary generation."}
        summary = await self.llm_client.complete(prompt)
        raw_output = summary
        yield {"type": "log", "message": "Summary generation finished."}

        if agent_type in CODE_GENERATING_AGENTS:
            if request.dryRun:
                validations.append("dryRun=true, skipped Codex execution")
                yield {"type": "status", "message": "dryRun=true, skipping Codex execution."}
            else:
                yield {"type": "status", "message": "Starting Codex execution."}
                codex_event_queue: asyncio.Queue[str] = asyncio.Queue()

                async def codex_sink(message: str) -> None:
                    """
                    AI Server 서비스 계층에서 `codex_sink()`가 맡는 sink 관련 작업을 수행한다.

                    주요 흐름은 `put()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

                    Args:
                        message: 출력하거나 전달할 메시지 문자열이다.
                    """
                    await codex_event_queue.put(message)

                runner_task = asyncio.create_task(
                    self.codex_runner.run(
                        prompt,
                        request.workspacePath,
                        event_sink=codex_sink,
                    )
                )

                while True:
                    try:
                        message = await asyncio.wait_for(codex_event_queue.get(), timeout=0.2)
                        yield {"type": "log", "message": message}
                        continue
                    except asyncio.TimeoutError:
                        if not runner_task.done():
                            continue

                    while not codex_event_queue.empty():
                        yield {"type": "log", "message": codex_event_queue.get_nowait()}
                    break

                codex_output, generated_files = await runner_task
                while not codex_event_queue.empty():
                    message = codex_event_queue.get_nowait()
                    yield {"type": "log", "message": message}
                summary = "\n".join([summary, "", codex_output]).strip()
                raw_output = codex_output
                validations.append("Codex execution applied")
                yield {"type": "status", "message": "Codex execution finished."}

        yield {
            "type": "complete",
            "response": AgentExecutionResponse(
                status="COMPLETED",
                summary=summary,
                executor=executor,
                generatedFiles=generated_files,
                validations=validations,
                promptPreview=prompt[:2000],
                rawOutput=raw_output,
            ).model_dump(),
        }
