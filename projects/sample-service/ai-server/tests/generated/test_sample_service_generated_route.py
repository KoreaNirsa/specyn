import asyncio
import importlib.util
from pathlib import Path

ROUTER_PATH = Path(__file__).resolve().parents[2] / "app" / "generated" / "sample_service" / "router.py"

def _load_generated_module():
    spec = importlib.util.spec_from_file_location("generated_sample_service_router", ROUTER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_generated_sample_service_context_route() -> None:
    module = _load_generated_module()
    payload = asyncio.run(module.generated_context())
    assert module.router.prefix == "/generated/sample-service"
    assert payload["projectId"] == "sample-service"
    assert payload["executionFlow"]
