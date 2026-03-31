from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5.2"
    codex_exec_mode: str = "disabled"
    codex_command_template: str = "codex exec --json --cwd {workspace}"
    codex_timeout_seconds: int = 900
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
        return Path(__file__).resolve().parents[4]

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.axb_cors_allowed_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
