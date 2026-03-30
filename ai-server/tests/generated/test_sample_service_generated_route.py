import pathlib
import sys

from fastapi.testclient import TestClient

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "ai-server"))

from app.main import app  # noqa: E402


client = TestClient(app)


def test_generated_sample_service_context_route() -> None:
    response = client.get("/generated/sample-service/context")
    assert response.status_code == 200
    payload = response.json()
    assert payload["projectId"] == "sample-service"
    assert payload["executionFlow"]
