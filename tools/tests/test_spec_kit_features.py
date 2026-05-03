from pathlib import Path

from tools.spec_loader import load_spec_bundle
from tools.validators import validate_bundle


SPEC_KIT_FEATURE_DIRS = [
    Path("specs/003-dashboard-design"),
    Path("specs/004-grill-me"),
    Path("specs/005-tdd-workflow"),
]


def test_spec_kit_feature_bundles_are_valid() -> None:
    for spec_dir in SPEC_KIT_FEATURE_DIRS:
        bundle = load_spec_bundle(spec_dir)
        assert validate_bundle(bundle) == [], spec_dir


def test_dashboard_design_bundle_contains_design_md() -> None:
    bundle = load_spec_bundle(Path("specs/003-dashboard-design"))

    assert "design" in bundle
    assert bundle["design"].name == "Design.md"
    assert "/workspace" in bundle["design"].raw_content


def test_tdd_workflow_records_red_green_refactor_gate() -> None:
    bundle = load_spec_bundle(Path("specs/005-tdd-workflow"))
    content = "\n".join(document.raw_content for document in bundle.values())

    assert "Red" in content
    assert "Green" in content
    assert "Refactor" in content
