---
id: sample-service-agent
type: agent
version: 1.4.1
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

## handoff 정책
- API와 backend는 contract를 공유한다.
- design과 frontend는 UX를 공유한다.
- review와 docs는 release readiness를 함께 확인한다.
- frontend는 source 코드, Vite build 설정, bundle 결과가 같은 React JSX runtime 계약을 따라야 한다.

## feedback 정책
- `execution_flow`는 기본 1차 실행 순서를 정의한다.
- `feedback_loops`는 1차 실행 이후 필요 시 되돌아갈 bounded loop를 정의한다.
- sample-service는 reference sample이므로 `max_feedback_rounds: 2` 범위 안에서만 반복한다.
- 반복은 drift 해소와 handoff 보강 목적이어야 하며 무한 루프처럼 동작해서는 안 된다.
- 사용자가 필요 시 직접 재실행할 수 있어야 한다.

# 출력
- execution flow
- feedback loop 계획
- validation ownership
- stop / retry policy

# 실행 규칙
1. `agent.md`는 orchestration의 source of truth다.
2. feedback loop는 `max_feedback_rounds` 범위 안에서만 반복할 수 있다.
3. sample-service는 unresolved 이슈를 줄이는 방향으로 bounded feedback를 수행한다.
4. docs는 실제 run command와 URL을 반영해야 한다.
5. frontend agent는 `React.createElement` 사용 여부와 React import/runtime 계약을 함께 맞춰야 한다.

# Validation 기준
- 필수 agent가 execution_flow에 포함되어 있어야 한다.
- feedback_loops와 supported_agents가 정합해야 한다.
- stop/retry 조건이 정의되어 있어야 한다.
- bounded feedback round 설정이 문서화되어 있어야 한다.
- frontend bootstrap 계약(`React is not defined` 방지)이 orchestration 관점에서 강조되어 있어야 한다.

# Prompt
## Role
당신은 Orchestrator Agent로서 sample-service 생성 흐름을 관리한다.

## Instructions
1. execution flow와 feedback loop를 정리한다.
2. handoff와 validation ownership을 명확히 적는다.
3. runtime 확인까지 이어지는 흐름을 유지한다.
4. unresolved 이슈가 남아 있으면 bounded feedback round 안에서 해결을 우선한다.
5. frontend 변경에서는 JSX runtime, React import, bundle bootstrap 오류를 unresolved 항목으로 남기지 않는다.

## Format
1. execution flow
2. feedback loop
3. validation ownership
4. stop and retry policy
