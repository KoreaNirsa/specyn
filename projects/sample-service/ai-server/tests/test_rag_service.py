import asyncio
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-server"))

from app.services.rag_service import RagService  # noqa: E402


def test_rag_service_returns_items() -> None:
    service = RagService()
    response = asyncio.run(service.search("spec validation", 3))
    assert len(response.items) > 0


def test_should_use_langchain_runtime_disabled_on_python_314() -> None:
    from app.services.rag_service import should_use_langchain_runtime

    assert should_use_langchain_runtime((3, 13)) is True
    assert should_use_langchain_runtime((3, 14)) is False
