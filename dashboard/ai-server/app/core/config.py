"""
AI Server가 `.env`와 기본값에서 읽어 올 런타임 설정을 정의하는 모듈이다.
Pydantic Settings를 기반으로 인증 방식, 모델 후보, RAG 크기, CORS origin 목록처럼 여러 서비스가 공유하는 설정을 중앙집중적으로 관리한다.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    환경 변수와 기본값을 기반으로 런타임 설정을 계산하는 설정 모델이다.

    상속 기반은 `BaseSettings`이다 / 외부에서 주로 읽어야 할 메서드는 `project_root()`, `cors_allowed_origins()`, `codex_model_candidates()`이다.

    Attributes:
        specyn_auth_mode: 인스턴스가 내부적으로 유지하는 specyn 인증 mode 관련 상태다.
        openai_api_key: 인스턴스가 내부적으로 유지하는 OpenAI API key 관련 상태다.
        openai_base_url: 인스턴스가 내부적으로 유지하는 OpenAI base URL 관련 상태다.
        openai_model: 인스턴스가 내부적으로 유지하는 OpenAI 모델 관련 상태다.
        codex_model: 인스턴스가 내부적으로 유지하는 Codex 모델 관련 상태다.
        codex_fallback_models: 인스턴스가 내부적으로 유지하는 Codex 대체 경로 모델 목록 관련 상태다.
        codex_exec_mode: 인스턴스가 내부적으로 유지하는 Codex exec mode 관련 상태다.
        codex_command_template: 인스턴스가 내부적으로 유지하는 Codex command 템플릿 관련 상태다.
        codex_timeout_seconds: 인스턴스가 내부적으로 유지하는 Codex 타임아웃 seconds 관련 상태다.
        codex_home: 인스턴스가 내부적으로 유지하는 Codex 홈 디렉터리 관련 상태다.
        rag_docs_dir: 인스턴스가 내부적으로 유지하는 RAG 문서 집합 dir 관련 상태다.
        rag_chunk_size: 인스턴스가 내부적으로 유지하는 RAG 청크 size 관련 상태다.
        rag_chunk_overlap: 인스턴스가 내부적으로 유지하는 RAG 청크 overlap 관련 상태다.
        prompt_snapshot_dir: 인스턴스가 내부적으로 유지하는 프롬프트 snapshot dir 관련 상태다.
        axb_cors_allowed_origins: 인스턴스가 내부적으로 유지하는 axb CORS origin 목록 allowed origin 목록 관련 상태다.
    """

    specyn_auth_mode: str = "chatgpt"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5.4"
    codex_model: str = "gpt-5.4"
    codex_fallback_models: str = "gpt-5.3-codex"
    codex_exec_mode: str = "cli"
    codex_command_template: str = "codex exec --json --model {model} --sandbox danger-full-access -C {workspace} --skip-git-repo-check"
    codex_timeout_seconds: int = 900
    codex_home: str = ".specyn/codex"
    rag_docs_dir: str = "docs"
    rag_chunk_size: int = 1200
    rag_chunk_overlap: int = 120
    prompt_snapshot_dir: str = ".specyn/prompts"
    axb_cors_allowed_origins: str = "http://localhost:4173,http://127.0.0.1:4173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def project_root(self) -> Path:
        """
        설정이나 객체 내부 상태에서 계산된 값을 프로퍼티 형태로 노출한다.

        주요 흐름은 `Path()`, `resolve()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

        Returns:
            계산된 파일 또는 디렉터리 경로 객체다.
        """
        return Path(__file__).resolve().parents[4]

    @property
    def cors_allowed_origins(self) -> list[str]:
        """
        설정이나 객체 내부 상태에서 계산된 값을 프로퍼티 형태로 노출한다.

        주요 흐름은 `strip()`, `split()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

        Returns:
            조건에 맞춰 수집하거나 정렬한 목록이다.
        """
        return [
            origin.strip()
            for origin in self.axb_cors_allowed_origins.split(",")
            if origin.strip()
        ]

    @property
    def codex_model_candidates(self) -> list[str]:
        """
        설정이나 객체 내부 상태에서 계산된 값을 프로퍼티 형태로 노출한다.

        주요 흐름은 `extend()`, `strip()`, `split()`, `append()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
        반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

        Returns:
            조건에 맞춰 수집하거나 정렬한 목록이다.
        """
        candidates = [self.codex_model]
        candidates.extend(
            model.strip()
            for model in self.codex_fallback_models.split(",")
            if model.strip()
        )
        unique: list[str] = []
        for model in candidates:
            if model not in unique:
                unique.append(model)
        return unique


@lru_cache
def get_settings() -> Settings:
    """
    프로젝트에서 `get_settings()`가 맡는 설정 관련 작업을 수행한다.

    주요 흐름은 `Settings()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        함수에서 조립한 `Settings` 타입 결과다.
    """
    return Settings()
