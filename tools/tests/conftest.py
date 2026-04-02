"""
pytest 실행 전에 테스트 경로와 공통 초기화 조건을 맞추기 위한 설정 모듈이다.
현재 저장소 루트를 `sys.path`에 추가해 테스트 코드가 패키지 import 경로 문제 없이 실제 모듈을 불러오도록 만든다.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
