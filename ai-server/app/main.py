from fastapi import FastAPI

from app.api.routes.agents import router as agents_router
from app.api.routes.health import router as health_router

app = FastAPI(
    title="Specyn AI Server",
    version="0.2.0",
    description="Prompt compilation, OpenAI Responses routing, Codex execution, optional LangChain RAG.",
)

app.include_router(health_router)
app.include_router(agents_router)
