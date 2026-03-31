# 기여 가이드

## 기본 원칙

- 문서는 한국어를 기본으로 작성합니다.
- 코드보다 spec를 먼저 수정합니다.
- 새 기능은 가능하면 예제 spec와 함께 제출합니다.
- agent catalog나 prompt 규칙을 바꾸면 테스트와 문서를 함께 갱신합니다.
- `feedback_loops`, 구조 규칙, prompt contract를 바꾸면 예제 spec와 validator도 함께 갱신합니다.
- 로컬에서 `make ci-local` 통과 후 PR을 생성하는 편이 좋습니다.

## 가장 권장하는 기여 유형

1. **bug fix**: quickstart, sample-flow, sample-service를 깨는 문제 해결
2. **docs improvement**: README, quickstart, playbook, comparison 문서 보강
3. **sample improvement**: sample-service 또는 새로운 reference sample 추가
4. **agent proposal**: 새 agent 역할이나 handoff 기준 제안
5. **use case 공유**: 실제 도입 사례, spec 작성 패턴, pain point 공유

## 권장 PR 흐름

1. 이슈 또는 논의 생성
2. spec 수정
3. code / test / docs 수정
4. `make ci-local` 실행
5. PR 생성

## PR 체크리스트

- [ ] README 또는 docs 반영 여부를 확인했습니다.
- [ ] spec 변경 시 예제/템플릿 정합성을 확인했습니다.
- [ ] agent flow / feedback loop 변경 시 테스트를 갱신했습니다.
- [ ] 구조 규칙(Spring Boot/FastAPI) 변경 시 README/docs를 반영했습니다.
- [ ] 테스트 또는 검증 근거를 첨부했습니다.
- [ ] sample-service 기준 실행 흐름을 깨뜨리지 않는지 확인했습니다.

## 브랜치 권장 규칙

- `feature/<topic>`
- `fix/<topic>`
- `docs/<topic>`

## 추가 체크

- docs/guide 링크가 깨지지 않았는지 확인합니다.
- sample-service 기준 실행 절차가 여전히 동작하는지 확인합니다.
- 테스트 변경 시 실행 로그나 근거를 PR에 첨부합니다.
- 큰 변경은 `agent_proposal` 또는 feature issue로 먼저 방향을 맞추는 편이 좋습니다.

## 질문이나 방향 논의는 어디서 하나요?

- bug: 버그 리포트 템플릿
- feature: 기능 요청 템플릿
- question: 사용 질문 템플릿
- use case: 실제 적용 사례/샘플 제안 템플릿
- agent proposal: agent 구조나 handoff 변경 제안 템플릿

Discussions가 활성화되면 큰 방향 논의는 Discussions로 이동하는 편이 좋습니다.
