"""
저장소 루트에서 `python specyn.py ...` 형식으로 호출할 수 있게 CLI 구현을 노출하는 얇은 엔트리포인트다.
실제 명령 처리 로직은 `tools.specyn.main()`에 있으며, 이 파일은 루트 실행 경험을 안정적으로 유지하기 위한 위임 레이어 역할만 수행한다.
"""

from tools.specyn import main


if __name__ == "__main__":
    raise SystemExit(main())
