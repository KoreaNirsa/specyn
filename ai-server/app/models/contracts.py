from typing import Any

from pydantic import BaseModel, Field


class SpecDocument(BaseModel):
    name: str
    type: str
    content: str


class AgentStepResult(BaseModel):
    agent: str
    status: str
    summary: str
    generatedFiles: list[str] = Field(default_factory=list)
    validations: list[str] = Field(default_factory=list)


class AgentExecutionRequest(BaseModel):
    agent: str
    projectId: str
    documents: list[SpecDocument]
    previousResults: list[AgentStepResult] = Field(default_factory=list)
    workspacePath: str | None = None
    dryRun: bool = True


class AgentExecutionResponse(BaseModel):
    status: str
    summary: str
    generatedFiles: list[str] = Field(default_factory=list)
    validations: list[str] = Field(default_factory=list)
    promptPreview: str | None = None
    rawOutput: str | None = None


class RagSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class RagSearchResponse(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)
