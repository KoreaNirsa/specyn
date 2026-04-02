"""
`rag service` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

import asyncio
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "dashboard" / "ai-server"))

from app.services.rag_service import RagService  # noqa: E402


def test_rag_service_returns_items() -> None:
    """
    회귀 테스트로서 `rag_service_returns_items` 시나리오를 검증한다.

    주요 흐름은 `RagService()`, `run()`, `search()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    service = RagService()
    response = asyncio.run(service.search("spec validation", 3))
    assert len(response.items) > 0


def test_should_use_langchain_runtime_disabled_on_python_314() -> None:
    """
    회귀 테스트로서 `should_use_langchain_runtime_disabled_on_python_314` 시나리오를 검증한다.

    주요 흐름은 `should_use_langchain_runtime()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    from app.services.rag_service import should_use_langchain_runtime

    assert should_use_langchain_runtime((3, 13)) is True
    assert should_use_langchain_runtime((3, 14)) is False
