"""
AI Server 요청/응답 본문에서 사용하는 Pydantic 계약 모델을 모아 둔 모듈이다.
라우터, 서비스, 프런트엔드가 동일한 필드 이름과 JSON 구조를 공유할 수 있도록 agent 실행과 RAG 검색 관련 페이로드를 명시적으로 정의한다.
"""

from typing import Any

from pydantic import BaseModel, Field


class SpecDocument(BaseModel):
    """
    문서 본문과 메타데이터를 함께 보관해 후속 단계가 재해석 없이 재사용할 수 있게 하는 모델이다.

    상속 기반은 `BaseModel`이다.

    Attributes:
        name: 인스턴스가 내부적으로 유지하는 name 관련 상태다.
        type: 인스턴스가 내부적으로 유지하는 타입 관련 상태다.
        content: 인스턴스가 내부적으로 유지하는 content 관련 상태다.
    """

    name: str
    type: str
    content: str


class AgentStepResult(BaseModel):
    """
    단일 실행 단계나 외부 호출 결과를 구조화해 전달하기 위한 결과 모델이다.

    상속 기반은 `BaseModel`이다.

    Attributes:
        agent: 처리 대상 agent 이름 또는 식별자다.
        status: 현재 단계의 상태 문자열이다.
        summary: 사용자에게 보여 줄 요약 문자열이다.
        generatedFiles: 인스턴스가 내부적으로 유지하는 생성 산출물 파일 목록 관련 상태다.
        validations: 인스턴스가 내부적으로 유지하는 validations 관련 상태다.
    """

    agent: str
    status: str
    summary: str
    generatedFiles: list[str] = Field(default_factory=list)
    validations: list[str] = Field(default_factory=list)


class AgentExecutionRequest(BaseModel):
    """
    HTTP 또는 서비스 호출 시 들어오는 요청 본문을 표현하는 계약 모델이다.

    상속 기반은 `BaseModel`이다.

    Attributes:
        agent: 처리 대상 agent 이름 또는 식별자다.
        projectId: 인스턴스가 내부적으로 유지하는 프로젝트 id 관련 상태다.
        documents: 요청에 포함된 spec 문서 목록이다.
        previousResults: 인스턴스가 내부적으로 유지하는 previous 결과 목록 관련 상태다.
        workspacePath: 인스턴스가 내부적으로 유지하는 워크스페이스 경로 관련 상태다.
        dryRun: 인스턴스가 내부적으로 유지하는 dry run 관련 상태다.
    """

    agent: str
    projectId: str
    documents: list[SpecDocument]
    previousResults: list[AgentStepResult] = Field(default_factory=list)
    workspacePath: str | None = None
    dryRun: bool = True


class AgentExecutionResponse(BaseModel):
    """
    HTTP 또는 서비스 호출 결과를 외부에 돌려줄 응답 계약 모델이다.

    상속 기반은 `BaseModel`이다.

    Attributes:
        status: 현재 단계의 상태 문자열이다.
        summary: 사용자에게 보여 줄 요약 문자열이다.
        executor: 인스턴스가 내부적으로 유지하는 실행기 관련 상태다.
        generatedFiles: 인스턴스가 내부적으로 유지하는 생성 산출물 파일 목록 관련 상태다.
        validations: 인스턴스가 내부적으로 유지하는 validations 관련 상태다.
        promptPreview: 인스턴스가 내부적으로 유지하는 프롬프트 preview 관련 상태다.
        rawOutput: 인스턴스가 내부적으로 유지하는 raw 출력 관련 상태다.
    """

    status: str
    summary: str
    executor: str = "openai"
    generatedFiles: list[str] = Field(default_factory=list)
    validations: list[str] = Field(default_factory=list)
    promptPreview: str | None = None
    rawOutput: str | None = None


class RagSearchRequest(BaseModel):
    """
    HTTP 또는 서비스 호출 시 들어오는 요청 본문을 표현하는 계약 모델이다.

    상속 기반은 `BaseModel`이다.

    Attributes:
        query: RAG 검색이나 조회에 사용할 질의 문자열이다.
        top_k: 반환할 상위 검색 결과 개수다.
    """

    query: str
    top_k: int = 5


class RagSearchResponse(BaseModel):
    """
    HTTP 또는 서비스 호출 결과를 외부에 돌려줄 응답 계약 모델이다.

    상속 기반은 `BaseModel`이다.

    Attributes:
        items: 인스턴스가 내부적으로 유지하는 items 관련 상태다.
    """

    items: list[dict[str, Any]] = Field(default_factory=list)
