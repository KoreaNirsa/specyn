from pathlib import Path

import pytest

from tools.spec_loader import load_spec_bundle


def test_load_spec_bundle() -> None:
    bundle = load_spec_bundle(Path("specs/projects/sample-service"))

    assert set(bundle.keys()) == {"product", "api", "test", "review", "agent"}
    assert bundle["product"].metadata["owner_agent"] == "planner"


def test_load_spec_bundle_raises_on_duplicate_type(tmp_path: Path) -> None:
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
