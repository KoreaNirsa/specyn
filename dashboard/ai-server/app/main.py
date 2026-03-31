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
