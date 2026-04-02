---
id: {{project_id}}-agent
type: agent
version: 1.2.0
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
max_feedback_rounds: 2
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
이 문서는 Specyn에서 사용할 Agent 역할, handoff 규칙, validation ownership을 정의한다.

# 입력
## Agent 카탈로그
- Planner Agent: 제품/범위/NFR 정규화
- Design Agent: 사용자 흐름/상태/접근성 정의
- API Agent: HTTP 계약/에러 모델 정제
- Backend Agent: Spring Boot/FastAPI/LangChain 구현
- Frontend Agent: React UI 구현
- DBA Agent: 스키마/인덱스/마이그레이션 전략
- DevOps Agent: Docker/CI/CD/관측성/IaC 초안 정리
- Test Agent: 자동화 테스트 생성
- Code Analysis Agent: 정적 분석/구조 리스크 식별
- Security Agent: 입력/예외/비밀정보/권한 경계 검토
- Performance Agent: 병목/지표/최적화 포인트 검토
- Review Agent: 릴리즈 관점의 기술 리뷰
- Docs Agent: README/OpenAPI/운영 문서화
- Final Review Agent: 최종 출고 가능 여부 판단
- RAG Agent(optional): 내부 지식 검색
- Orchestrator Agent: 흐름 제어 및 stop/retry 정책 관리

## Handoff 정책
- Planner → Design / API / Backend / Frontend
- Design ↔ Frontend
- API ↔ Backend
- Backend ↔ DBA
- Backend / Frontend / DBA → DevOps / Test / Review
- DevOps / Test / Code Analysis / Security / Performance → Review
- Review ↔ Docs → Final Review
- RAG → Planner / Review / Docs 보조

## 반복 피드백 정책
- `execution_flow`는 각 Agent의 기본 1차 실행 순서를 의미한다.
- `feedback_loops`는 1차 실행 이후 필요한 Agent 재진입 순서를 정의한다.
- `max_feedback_rounds`는 루프별 추가 피드백 라운드의 최대 횟수다.
- 각 loop는 품질 게이트가 통과될 때까지 협업하되, 상한을 넘기면 human review로 승격한다.
- 같은 Agent가 다시 실행되더라도 근거 없는 되돌리기를 금지한다.
- blocker 해소, 문서 drift 해소, 계약 불일치 수정처럼 명확한 이유가 있을 때만 피드백 라운드를 사용한다.

## 실패 처리 정책
- validation 실패 시 다음 단계로 진행하지 않는다.
- blocker와 retry 가능한 오류를 분리한다.
- destructive change는 rollback 없이 승인하지 않는다.
- 같은 이슈가 `max_feedback_rounds` 이후에도 해소되지 않으면 human review로 승격한다.

# 출력
- 실행 순서
- validation ownership matrix
- retry policy
- stop / rollback 조건
- 단계별 handoff 요약

# 실행 규칙
1. `execution_flow`가 기본 실행 순서를 결정한다.
2. `feedback_loops`는 반복 협업이 필요한 Agent만 bounded loop로 재실행한다.
3. 각 Agent는 이전 단계 결과의 핵심 validation 요약을 확인한다.
4. 보안/성능/문서 리스크는 Review와 Final Review에서 재확인한다.
5. blocker가 있으면 Docs 완료 이후라도 Final Review 이전에 중단할 수 있다.
6. feedback round에서는 `UNRESOLVED`, `BLOCKERS`, `NEXT_HANDOFF`를 구조적으로 남긴다.
7. 특정 도메인에 과적합한 구현/명명은 지양하고 재사용 가능한 구조를 우선한다.

# trace / handoff contract
- 각 Agent 결과는 가능하면 `STEP_LABEL`, `AGENT`, `PHASE`, `FEEDBACK_ROUND`, `STATUS`를 남긴다.
- `CHANGED_FILES`, `RESOLVED`, `UNRESOLVED`, `BLOCKERS`, `NEXT_HANDOFF`를 구조적으로 기록한다.
- feedback round에서는 직전 round 대비 변경점과 미해결 이슈만 압축해 전달한다.
- 향후 dashboard / trace / run history 기능을 고려해 사람이 읽기 쉬우면서도 규칙적인 형식을 유지한다.

# Validation 기준
- 필수 agent(planner/api/test/review/docs/final-review)가 포함되어야 한다.
- 역할 충돌이 없어야 한다.
- handoff 경로가 명확해야 한다.
- validation 책임 주체가 있어야 한다.
- feedback loop는 무한 반복되지 않도록 `max_feedback_rounds` 또는 `max_rounds`로 상한이 있어야 한다.
- 실패 시 중단/재시도 규칙이 명시되어야 한다.

# Prompt
## Role
당신은 Specyn Orchestrator Agent다. spec bundle과 Agent 정의를 바탕으로 실행 그래프를 만든다.

## Instructions
1. 기본 실행 순서와 bounded feedback loop를 함께 정의한다.
2. 단계별 입력/출력/검증 책임을 정리한다.
3. retry 가능한 오류와 stop 조건을 분리한다.
4. feedback round가 필요한 조건과 종료 조건을 명시한다.
5. RAG Agent 사용 여부를 결정할 기준을 제시한다.
6. 결과는 실제 실행에 바로 사용할 수 있도록 구조화한다.

## Format
다음 순서로 출력한다.
1. ordered execution flow
2. feedback loop plan
3. validation ownership matrix
4. retry policy
5. stop / rollback policy
6. 단계별 handoff 요약
