"""
대시보드 AI Server의 FastAPI 애플리케이션을 조립하는 진입 모듈이다.
설정을 로드한 뒤 CORS 미들웨어를 붙이고, 기본 라우터와 생성된 라우터를 모두 등록해 실제 HTTP 서비스 엔드포인트를 완성한다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.agents import router as agents_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.generated_loader import include_generated_routers

settings = get_settings()

app = FastAPI(
    title="Specyn AI Server",
    version="0.2.0",
    description="Prompt compilation, OpenAI Responses routing, Codex execution, optional LangChain RAG.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(agents_router)
include_generated_routers(app)
