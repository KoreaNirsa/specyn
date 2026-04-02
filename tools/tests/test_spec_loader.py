"""
`spec loader` 관련 동작이 회귀 없이 유지되는지 확인하는 테스트 모듈이다.
정상 경로와 실패 경로를 함께 고정해 리팩터링 시 계약이 조용히 바뀌지 않도록 감시하는 역할을 한다.
"""

from pathlib import Path

import pytest

from tools.spec_loader import load_spec_bundle


def test_load_spec_bundle() -> None:
    """
    회귀 테스트로서 `load_spec_bundle` 시나리오를 검증한다.

    주요 흐름은 `load_spec_bundle()`, `keys()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    """
    bundle = load_spec_bundle(Path("specs/projects/sample-service"))

    assert set(bundle.keys()) == {"product", "api", "test", "review", "agent"}
    assert bundle["product"].metadata["owner_agent"] == "planner"


def test_load_spec_bundle_raises_on_duplicate_type(tmp_path: Path) -> None:
    """
    회귀 테스트로서 `load_spec_bundle_raises_on_duplicate_type` 시나리오를 검증한다.

    주요 흐름은 `raises()`, `load_spec_bundle()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        tmp_path: 파일 시스템 경로 객체다.
    """
    first = tmp_path / "product.md"
    second = tmp_path / "another-product.md"

    body = """---
id: sample-product
type: product
version: 1.0.0
owner_agent: planner
status: draft
depends_on: []
---

# 목적
text
# 입력
text
# 출력
text
# 실행 규칙
text
# Validation 기준
text
# Prompt
## Role
text
## Instructions
text
## Format
text
"""
    first.write_text(body, encoding="utf-8")
    second.write_text(body.replace("sample-product", "sample-product-2"), encoding="utf-8")

    with pytest.raises(ValueError):
        load_spec_bundle(tmp_path)
