"""
agent 실행과 RAG 검색을 외부 HTTP API로 노출하는 FastAPI 라우터 모듈이다.
요청 검증은 Pydantic 계약 모델에 맡기고, 실제 실행/검색 로직은 서비스 계층으로 위임해 라우트가 얇은 orchestration 레이어로 남도록 설계되어 있다.
"""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.contracts import (
    AgentExecutionRequest,
    AgentExecutionResponse,
    RagSearchRequest,
    RagSearchResponse,
)
from app.services.agent_service import AgentService
from app.services.rag_service import RagService

router = APIRouter(prefix="/v1", tags=["agents"])

agent_service = AgentService()
rag_service = RagService()


@router.post("/agents/execute", response_model=AgentExecutionResponse)
async def execute_agent(request: AgentExecutionRequest) -> AgentExecutionResponse:
    """
    FastAPI 라우터에서 요청을 받아 서비스 계층으로 위임하는 엔드포인트 핸들러다.

    주요 흐름은 `post()`, `execute()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        request: HTTP 요청 본문 또는 agent 실행 요청 모델이다.

    Returns:
        함수에서 조립한 `AgentExecutionResponse` 타입 결과다.
    """
    return await agent_service.execute(request)


@router.post("/agents/execute/stream")
async def stream_execute_agent(request: AgentExecutionRequest) -> StreamingResponse:
    """
    FastAPI 라우터에서 요청을 받아 서비스 계층으로 위임하는 엔드포인트 핸들러다.

    주요 흐름은 `post()`, `execute_stream()`, `StreamingResponse()`, `event_stream()`를 이용해 이벤트를 만들고, 이를 순차적으로 스트리밍하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        request: HTTP 요청 본문 또는 agent 실행 요청 모델이다.

    Yields:
        호출 순서에 따라 외부 소비자가 이어서 처리할 이벤트 또는 스트림 항목이다.
    """

    async def event_stream():
        """
        FastAPI 라우터 계층에서 `event_stream()`가 맡는 스트림 관련 작업을 수행한다.

        주요 흐름은 `execute_stream()`를 이용해 이벤트를 만들고, 이를 순차적으로 스트리밍하는 것이다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Yields:
            호출 순서에 따라 외부 소비자가 이어서 처리할 이벤트 또는 스트림 항목이다.
        """
        async for event in agent_service.execute_stream(request):
            yield json.dumps(event, ensure_ascii=False) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@router.post("/rag/search", response_model=RagSearchResponse)
async def rag_search(request: RagSearchRequest) -> RagSearchResponse:
    """
    FastAPI 라우터에서 요청을 받아 서비스 계층으로 위임하는 엔드포인트 핸들러다.

    주요 흐름은 `post()`, `search()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        request: HTTP 요청 본문 또는 agent 실행 요청 모델이다.

    Returns:
        함수에서 조립한 `RagSearchResponse` 타입 결과다.
    """
    return await rag_service.search(request.query, request.top_k)
