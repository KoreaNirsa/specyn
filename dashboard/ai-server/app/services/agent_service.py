import json

from app.core.config import get_settings
from app.models.contracts import AgentExecutionRequest, AgentExecutionResponse
from app.services.codex_runner import CodexRunner
from app.services.openai_responses_client import OpenAIResponsesClient
from app.services.prompt_builder import PromptBuilder
from app.services.rag_service import RagService

CODE_GENERATING_AGENTS = {"API", "BACKEND", "FRONTEND", "DBA", "DEVOPS", "TEST", "DOCS"}


def normalize_agent_name(agent_name: str) -> str:
    return agent_name.strip().lower().replace("_", "-")


def agent_key(agent_name: str) -> str:
    return normalize_agent_name(agent_name).replace("-", "_").upper()


class AgentService:
    def __init__(self) -> None:
        settings = get_settings()
        self.prompt_builder = PromptBuilder()
        self.llm_client = OpenAIResponsesClient(settings)
        self.codex_runner = CodexRunner(settings)
        self.rag_service = RagService()

    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResponse:
        prompt = self.prompt_builder.build(request)
        normalized_agent = normalize_agent_name(request.agent)
        agent_type = agent_key(request.agent)

        validations = [
            "spec bundle 수신 완료",
            f"agent={normalized_agent} prompt 조합 완료",
            f"previousResults={len(request.previousResults)}건 반영",
        ]

        generated_files: list[str] = []
        raw_output = ""

        if agent_type == "RAG":
            query = (
                f"{request.projectId} architecture spec review testing quality security performance"
            )
            rag_response = await self.rag_service.search(query, 5)
            summary_lines = [
                "[rag-results] 아래 문서를 다음 단계 근거로 사용합니다.",
                *[
                    f"- {item['source']} (score={item['score']}): {item['content'][:140]}"
                    for item in rag_response.items
                ],
            ]
            summary = "\n".join(summary_lines)
            raw_output = json.dumps(rag_response.model_dump(), ensure_ascii=False, indent=2)
            validations.append("RAG 검색 완료")
            return AgentExecutionResponse(
                status="COMPLETED",
                summary=summary,
                generatedFiles=generated_files,
                validations=validations,
                promptPreview=prompt[:2000],
                rawOutput=raw_output,
            )

        summary = await self.llm_client.complete(prompt)
        raw_output = summary

        if agent_type in CODE_GENERATING_AGENTS:
            if request.dryRun:
                validations.append("dryRun=true 이므로 Codex 실행을 건너뜀")
            else:
                codex_output, generated_files = await self.codex_runner.run(
                    prompt, request.workspacePath
                )
                summary = "\n".join([summary, "", codex_output]).strip()
                raw_output = codex_output
                validations.append("Codex 실행 단계 반영")

        return AgentExecutionResponse(
            status="COMPLETED",
            summary=summary,
            generatedFiles=generated_files,
            validations=validations,
            promptPreview=prompt[:2000],
            rawOutput=raw_output,
        )
