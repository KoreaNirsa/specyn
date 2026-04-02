"""
CI 파이프라인에서 sample-service spec bundle의 유효성을 빠르게 점검하는 검사 엔트리포인트다.
`load_spec_bundle()`로 문서를 읽고 `validate_bundle()`로 규칙 위반을 수집한 뒤, 사람이 읽기 쉬운 로그와 종료 코드로 결과를 반환한다.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.spec_loader import load_spec_bundle
from tools.validators import validate_bundle


def main() -> int:
    """
    CI 검사 단계에서 메인 진입점 역할을 수행한다.

    주요 흐름은 `load_spec_bundle()`, `validate_bundle()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    bundle = load_spec_bundle(ROOT / "specs/projects/sample-service")
    issues = validate_bundle(bundle)

    if issues:
        for issue in issues:
            print(f"[{issue.level}] {issue.code}: {issue.message}")
        return 1

    print("SPEC_BUNDLE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
