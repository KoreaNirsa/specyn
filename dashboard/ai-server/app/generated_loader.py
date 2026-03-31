from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Iterable

from fastapi import APIRouter, FastAPI

GENERATED_ROOT = Path(__file__).resolve().parent / "generated"


def iter_generated_router_modules() -> Iterable[str]:
    if not GENERATED_ROOT.exists():
        return []
    modules: list[str] = []
    for path in sorted(GENERATED_ROOT.iterdir()):
        if not path.is_dir() or path.name.startswith("_"):
            continue
        if not (path / "router.py").exists():
            continue
        modules.append(f"app.generated.{path.name}.router")
    return modules


def include_generated_routers(app: FastAPI) -> None:
    for module_name in iter_generated_router_modules():
        module = import_module(module_name)
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            app.include_router(router)
