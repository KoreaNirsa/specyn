# 기여 가이드

## 기본 원칙
- 문서는 한국어를 기본으로 작성합니다.
- 코드보다 spec를 먼저 수정합니다.
- 새 기능은 가능하면 예제 spec와 함께 제출합니다.
- agent catalog나 prompt 규칙을 바꾸면 테스트와 문서를 함께 갱신합니다.
- `feedback_loops`, 구조 규칙, prompt contract를 바꾸면 예제 spec와 validator도 함께 갱신합니다.
- 로컬에서 `make ci-local` 통과 후 PR을 생성합니다.

## 권장 PR 흐름
1. 이슈 또는 논의 생성
2. spec 수정
3. code / test / docs 수정
4. `make ci-local` 실행
5. PR 생성

## PR 체크리스트
- [ ] README 또는 docs 반영 여부 확인
- [ ] spec 변경 시 예제/템플릿 정합성 확인
- [ ] agent flow / feedback loop 변경 시 테스트 갱신
- [ ] 구조 규칙(Spring Boot/FastAPI) 변경 시 README/docs 반영
- [ ] 테스트 또는 검증 근거 첨부
- [ ] 한국어 문서 기준 유지

## 브랜치 권장 규칙
- `feature/<topic>`
- `fix/<topic>`
- `docs/<topic>`
