---
id: todo-service-agent
type: agent
version: 1.1.0
owner_agent: orchestrator
status: draft
depends_on: [product, api, test, review]
execution_flow:
  - planner
  - design
  - api
  - backend
  - frontend
  - dba
  - devops
  - test
  - code-analysis
  - security
  - performance
  - review
  - docs
  - final-review
max_feedback_rounds: 1
feedback_loops:
  - name: api-backend-contract-sync
    trigger_after: backend
    agents:
      - api
      - backend
  - name: design-frontend-ux-sync
    trigger_after: frontend
    agents:
      - design
      - frontend
  - name: backend-dba-persistence-hardening
    trigger_after: dba
    agents:
      - backend
      - dba
  - name: review-docs-release-sync
    trigger_after: docs
    agents:
      - review
      - docs
optional_agents:
  - rag
supported_agents:
  - planner
  - design
  - api
  - backend
  - frontend
  - dba
  - devops
  - test
  - code-analysis
  - security
  - performance
  - review
  - docs
  - final-review
  - rag
  - orchestrator
---

# 목적
Todo 서비스 생성 시 사용할 Agent 역할과 handoff 규칙을 정의한다.

# 입력
## Agent 목록
- Planner Agent
- Design Agent
- API Agent
- Backend Agent
- Frontend Agent
- DBA Agent
- DevOps Agent
- Test Agent
- Code Analysis Agent
- Security Agent
- Performance Agent
- Review Agent
- Docs Agent
- Final Review Agent
- Orchestrator Agent
- RAG Agent(optional)

## Handoff 정책
- Planner → Design / API / Backend / Frontend
- Design ↔ Frontend
- API ↔ Backend
- Backend ↔ DBA
- Backend / Frontend / DBA → DevOps / Test / Review
- DevOps / Test / Code Analysis / Security / Performance → Review
- Review ↔ Docs → Final Review
- RAG → Planner / Review 보조

## 반복 피드백 정책
- `execution_flow`는 각 Agent의 기본 1차 실행 순서를 의미한다.
- `feedback_loops`는 1차 실행 이후 필요한 Agent 재진입 순서를 정의한다.
- `max_feedback_rounds: 1` 이므로 동일 루프는 추가 1회까지만 반복한다.
- 같은 Agent가 다시 실행되더라도 근거 없는 되돌리기를 금지한다.
- blocker 해소, 문서 drift 해소, 계약 불일치 수정 같은 명확한 이유가 있을 때만 피드백 라운드를 사용한다.

## 실패 처리 정책
- validation 실패 시 다음 단계로 진행하지 않는다.
- blocker가 있으면 flow를 중단한다.
- destructive change는 rollback 방향 없이 승인하지 않는다.
- 같은 이슈가 추가 피드백 라운드 이후에도 남아 있으면 human review로 승격한다.

# 출력
- 실행 순서
- validation ownership
- 실패 시 재시도 정책
- 최종 승인 조건

# 실행 규칙
1. 이전 Agent의 validation 실패 시 다음 Agent로 진행하지 않는다.
2. `feedback_loops`는 bounded loop로만 허용한다.
3. Docs Agent는 Review 완료 이후에만 실행한다.
4. Final Review Agent는 기술/문서/운영 리스크를 종합한다.
5. handoff에는 핵심 요약과 남은 리스크를 포함한다.

# trace / handoff contract
- 각 Agent 결과는 가능하면 `STEP_LABEL`, `AGENT`, `PHASE`, `FEEDBACK_ROUND`, `STATUS`를 남긴다.
- `CHANGED_FILES`, `RESOLVED`, `UNRESOLVED`, `BLOCKERS`, `NEXT_HANDOFF`를 구조적으로 기록한다.
- feedback round에서는 직전 round 대비 변경점과 미해결 이슈만 압축해 전달한다.
- 향후 dashboard / trace / run history 기능을 고려해 사람이 읽기 쉬우면서도 규칙적인 형식을 유지한다.

# Validation 기준
- 역할 중복이 없어야 한다.
- handoff 흐름이 끊기지 않아야 한다.
- validation 책임 주체가 있어야 한다.
- stop 조건이 명확해야 한다.
- execution_flow에 필수 agent(planner/api/test/review/docs/final-review)가 포함되어야 한다.
- feedback loop에 상한이 있어야 한다.

# Prompt
## Role
당신은 Specyn Orchestrator Agent다. Todo 서비스용 실행 그래프와 검증 책임을 설계한다.

## Instructions
1. 기본 실행 순서와 bounded feedback loop를 함께 정의한다.
2. 단계별 validation ownership을 정리한다.
3. retry 가능한 오류와 stop 조건을 구분한다.
4. Docs/Final Review 실행 조건을 명시한다.
5. feedback round 종료 조건을 명시한다.
6. 결과를 실제 multi-agent 실행에 바로 사용할 수 있도록 구조화한다.

## Format
1. ordered execution flow
2. feedback loop plan
3. validation ownership matrix
4. retry policy
5. stop policy
6. 단계별 handoff 요약
