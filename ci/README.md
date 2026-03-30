# CI 보조 스크립트

`ci/`는 GitHub Actions와 유사한 검증 흐름을 로컬에서 재현하기 위한 스크립트를 담는다.

## 포함 내용
- `check_spec_bundle.py`: 예제 spec bundle 유효성 검사
- `local-ci.sh`: 로컬 통합 검증 실행

## 원칙
- 예제 spec는 항상 유효해야 한다.
- 로컬 검증과 GitHub Actions 검증은 가능한 한 동일해야 한다.
- CI 범위는 **빌드/테스트/포맷/spec validation** 까지로 제한한다.
- agent flow와 prompt 규칙이 바뀌면 예제 bundle과 테스트를 함께 갱신한다.
