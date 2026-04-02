"""
생성된 AI Server 라우터를 동적으로 탐색하고 FastAPI 앱에 포함시키는 로더 모듈이다.
`app/generated/<project>/router.py` 규약을 기준으로 import 대상을 찾기 때문에, 생성 산출물과 런타임 서버 사이의 연결 지점을 담당한다고 볼 수 있다.
"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Iterable

from fastapi import APIRouter, FastAPI

GENERATED_ROOT = Path(__file__).resolve().parent / "generated"


def iter_generated_router_modules() -> Iterable[str]:
    """
    프로젝트에서 생성 산출물 라우터 modules을(를) 순회하거나 열거한다.

    주요 흐름은 `iterdir()`, `is_dir()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    여러 조건 분기가 있어 실행 환경, 설정 값, 파일 존재 여부, 요청 형태에 따라 처리 경로가 달라진다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Returns:
        함수에서 조립한 `Iterable[str]` 타입 결과다.
    """
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
    """
    프로젝트에서 생성 산출물 라우터 목록을(를) 현재 실행 컨텍스트에 포함시킨다.

    주요 흐름은 `iter_generated_router_modules()`, `import_module()`, `include_router()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Args:
        app: 라우터를 등록하거나 상태를 구성할 FastAPI 애플리케이션 인스턴스다.
    """
    for module_name in iter_generated_router_modules():
        module = import_module(module_name)
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            app.include_router(router)
