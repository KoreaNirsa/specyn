from fastapi import APIRouter

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
    return await agent_service.execute(request)


@router.post("/rag/search", response_model=RagSearchResponse)
async def rag_search(request: RagSearchRequest) -> RagSearchResponse:
    return await rag_service.search(request.query, request.top_k)
