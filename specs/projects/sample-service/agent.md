---
id: sample-service-agent
type: agent
version: 1.3.0
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
sample-service를 생성하기 위한 agent execution flow와 handoff 규칙을 정의한다.

# 입력
## 필수 agent
- planner
- api
- test
- review
- docs
- final-review

## handoff 원칙
- API와 backend는 contract를 공유한다.
- design과 frontend는 UX를 공유한다.
- review와 docs는 release readiness를 함께 확인한다.

# 출력
- execution flow
- feedback loop 계획
- validation ownership

# 실행 규칙
1. agent.md는 orchestration의 source of truth다.
2. feedback loop는 max_feedback_rounds 범위 안에서만 재진입한다.
3. docs는 실제 run command와 URL을 반영해야 한다.

# Validation 기준
- 필수 agent가 execution_flow에 포함되어야 한다.
- feedback_loops와 supported_agents가 정합해야 한다.
- stop/retry 조건이 정의되어야 한다.

# Prompt
## Role
당신은 Orchestrator Agent다. sample-service 생성 흐름을 관리한다.

## Instructions
1. execution flow와 feedback loop를 정리한다.
2. handoff와 validation ownership을 명확히 한다.
3. runtime 확인까지 이어지는 흐름을 유지한다.

## Format
1. execution flow
2. feedback loop
3. validation ownership
4. stop and retry policy
