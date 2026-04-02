"""
과거 진입점 이름을 유지하면서 현재 CLI 구현으로 위임하기 위한 호환용 엔트리포인트다.
저장소 외부 스크립트가 `tools/ax_builder.py`를 호출해도 결국 `tools.specyn.main()`을 실행하도록 연결한다.
"""

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.specyn import main


if __name__ == "__main__":
    raise SystemExit(main())
