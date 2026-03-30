from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.spec_loader import load_spec_bundle
from tools.validators import validate_bundle


def main() -> int:
    bundle = load_spec_bundle(ROOT / "specs/examples/todo-service")
    issues = validate_bundle(bundle)

    if issues:
        for issue in issues:
            print(f"[{issue.level}] {issue.code}: {issue.message}")
        return 1

    print("SPEC_BUNDLE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
