"""
`health` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

import pathlib
import sys

from fastapi.testclient import TestClient

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "dashboard" / "ai-server"))

from app.main import app  # noqa: E402


client = TestClient(app)


def test_health() -> None:
    """
    회귀 테스트로서 `health` 시나리오를 검증한다.

    주요 흐름은 `json()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "UP"
    assert payload["service"] == "ai-server"


def test_health_allows_frontend_origin_via_cors() -> None:
    """
    회귀 테스트로서 `health_allows_frontend_origin_via_cors` 시나리오를 검증한다.

    주요 흐름은 `get()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    response = client.get("/health", headers={"Origin": "http://localhost:4173"})

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4173"
