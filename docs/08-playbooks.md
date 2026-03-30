# 08. Playbooks

## 초급 플레이북: 구조 이해가 목표인 경우

### 추천 순서
1. `bootstrap`
2. `doctor`
3. `validate-spec`
4. `compile-prompts`
5. `run-sim`
6. 예제 spec와 generated prompt를 직접 읽기

### 여기서 확인해야 할 것
- spec가 어떻게 생겼는지
- agent.md가 왜 중요한지
- prompt가 어떤 순서로 컴파일되는지
- 실행하지 않아도 어디까지 검증 가능한지

## 중급 플레이북: 내 프로젝트에 맞게 spec를 바꾸는 경우

### 추천 순서
1. `init-spec`
2. `product.md`부터 작성
3. `api.md`, `test.md`, `review.md` 작성
4. `api.md`에 구조 규칙(Spring Boot `global/common/domain`, FastAPI `app/global/common/domain`)을 기록
5. `agent.md`에서 필요한 agent와 `feedback_loops`를 선택
6. `validate`
7. `compile-prompts`
8. `run --workspace ...`

### 팁
- 처음부터 모든 agent를 다 켜지 않아도 된다.
- 다만 core quality gate(planner/api/test/review/docs/final-review)는 유지하는 편이 안정적이다.
- 초기에는 RAG보다 spec 품질을 먼저 높이는 것이 더 중요하다.
- feedback loop는 1개 또는 2개 정도의 핵심 경계부터 시작하는 편이 안전하다.

## 고급 플레이북: 현업 프로덕션 흐름에 붙이는 경우

### 추천 순서
1. Codex CLI 연동
2. 팀 문서를 RAG 대상에 포함
3. artifact/log 저장 정책 수립
4. branch-per-run 또는 PR bot 전략 도입
5. CI에서 spec validation + review gate 강화
6. queue/runner 구조로 비동기화

### 조직 적용 시 체크포인트
- secret 관리
- workspace 격리
- 감사 추적 로그
- human review gate
- 비용/성능 모니터링
- rollback 전략

## 상황별 예시

### 백엔드 API 중심
- agent.md에서 frontend/design을 제외하고 backend/security/test 중심으로 구성

### 풀스택 서비스
- design/frontend/backend/dba/devops/test/review/docs를 모두 포함

### 사내 AX Builder
- planner 앞뒤로 RAG, devops, docs, final-review를 강화


### 패키지 구조 기준이 중요한 백엔드/AI 서비스
- `api.md`에 Spring Boot `global / common / domain` 또는 FastAPI `app/global / app/common / app/domain` 구조를 먼저 고정
- Review Agent가 구조 drift를 판별하기 쉬워진다.
