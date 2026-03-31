from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "UP",
        "service": "ai-server",
        "model": settings.openai_model,
        "codexMode": settings.codex_exec_mode,
    }
