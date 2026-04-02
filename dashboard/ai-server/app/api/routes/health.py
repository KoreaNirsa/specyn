"""
AI Server의 생존 여부를 빠르게 확인하기 위한 헬스체크 라우터 모듈이다.
대시보드 프런트엔드와 자동화 테스트가 최소 비용으로 서버 가용성을 판별할 수 있도록 단순한 JSON 응답만 제공한다.
"""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """
    FastAPI 라우터에서 요청을 받아 서비스 계층으로 위임하는 엔드포인트 핸들러다.

    주요 흐름은 `get_settings()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Returns:
        키 기반으로 정리한 매핑 결과다.
    """
    settings = get_settings()
    return {
        "status": "UP",
        "service": "ai-server",
        "authMode": settings.specyn_auth_mode,
        "model": settings.openai_model,
        "codexModel": settings.codex_model,
        "codexFallbackModels": ",".join(settings.codex_model_candidates[1:]),
        "codexMode": settings.codex_exec_mode,
    }
