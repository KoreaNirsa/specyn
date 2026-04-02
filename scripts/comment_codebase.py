"""
저장소 전반의 소스 파일을 순회하면서 자동 주석 대상 파일을 찾아 일괄 주석 작업을 수행하는 스크립트다.
`tools.code_comments` 모듈을 감싼 얇은 실행 진입점으로, 어떤 파일이 실제로 수정되었는지 요약까지 함께 출력한다.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from tools.code_comments import annotate_paths, should_annotate_path


def iter_code_paths(root_dir: Path) -> list[Path]:
    """
    스크립트 계층에서 코드 경로 목록을(를) 순회하거나 열거한다.

    주요 흐름은 `rglob()`, `is_file()`, `should_annotate_path()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.

    Args:
        root_dir: 검색을 시작할 저장소 루트 경로다.

    Returns:
        계산된 파일 또는 디렉터리 경로 객체다.
    """
    return sorted(path for path in root_dir.rglob("*") if path.is_file() and should_annotate_path(path))


def main() -> int:
    """
    스크립트 계층에서 메인 진입점 역할을 수행한다.

    주요 흐름은 `iter_code_paths()`, `annotate_paths()`를 차례로 사용해 입력을 정리하고 결과를 조립하는 것이다.
    반복문을 사용해 여러 항목을 누적하거나 후보를 순차적으로 평가한다.

    Returns:
        호출자가 그대로 사용할 수 있는 종료 코드 또는 정수 결과다.
    """
    paths = iter_code_paths(ROOT_DIR)
    changed_paths = annotate_paths(paths)
    print(f"ANNOTATED {len(changed_paths)} FILES")
    for path in changed_paths:
        print(path.relative_to(ROOT_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
