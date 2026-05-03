export const DEFAULT_DOCS = {
  spec: `---
id: sample-service-product
type: product
version: 1.3.0
owner_agent: planner
status: draft
depends_on: []
---

# 목적
sample-service를 spec 기반으로 생성하고 실행까지 확인할 수 있는 reference CRUD project 요구사항을 정의한다.

# 입력
## 배경
- dashboard에서 spec bundle을 편집하고 agent를 실행하면 sample-service code가 생성되어야 한다.
- 생성된 sample-service는 frontend, backend, ai-server를 포함한 runnable project여야 한다.

## 핵심 시나리오
1. 사용자가 task를 생성한다.
2. 사용자가 task 목록과 detail을 확인한다.
3. 사용자가 task status를 PENDING 또는 DONE으로 변경한다.
4. 사용자가 task를 삭제한다.
5. 사용자가 generated runtime을 직접 실행하고 동작을 확인한다.

## 비기능 요구사항
- dashboard와 sample-service의 역할이 분리되어야 한다.
- sample-service runtime은 local 환경에서 바로 실행 가능해야 한다.
- validation 오류는 사람이 읽을 수 있는 메시지로 보여야 한다.

# 출력
- sample-service가 만족해야 하는 product 요구사항
- downstream spec이 재사용할 용어와 acceptance criteria

# 실행 규칙
1. sample-service는 완성된 template가 아니라 agent 산출물이다.
2. generated code는 projects/sample-service 아래에 기록한다.
3. generated runtime에서 CRUD 흐름이 끝까지 동작해야 한다.

# Validation 기준
- 핵심 시나리오가 3개 이상 있어야 한다.
- 비기능 요구사항이 포함되어야 한다.
- output과 execution rule이 명확해야 한다.

# Prompt
## Role
당신은 Planner Agent다. sample-service를 reference sample로 정의한다.

## Instructions
1. product 요구사항과 acceptance criteria를 정리한다.
2. downstream agent가 사용할 용어를 고정한다.
3. runtime 확인 포인트를 포함한다.

## Format
1. 작업 요약
2. 도메인 용어
3. acceptance criteria
4. runtime 확인 포인트
`,
  api: `---
id: sample-service-api
type: api
version: 1.3.0
owner_agent: api
status: draft
depends_on: [product]
---

# 목적
sample-service CRUD 기능에 필요한 API contract를 정의한다.

# 입력
## API 목록
- GET /api/v1/tasks
- GET /api/v1/tasks/{id}
- POST /api/v1/tasks
- PATCH /api/v1/tasks/{id}/status
- DELETE /api/v1/tasks/{id}

## 제약
- title은 required다.
- status는 PENDING, DONE만 허용한다.
- not found는 404를 사용한다.

# 출력
- request/response 구조
- status code 정책
- error response 규칙

# 실행 규칙
1. API contract는 generated frontend와 backend가 함께 사용한다.
2. placeholder endpoint를 남기지 않는다.
3. error payload는 code, message, path, timestamp를 포함한다.

# Validation 기준
- 모든 endpoint가 정의되어 있어야 한다.
- success와 failure case가 있어야 한다.
- status와 payload 구조가 일관돼야 한다.

# Prompt
## Role
당신은 API Agent다. sample-service CRUD API contract를 정리한다.

## Instructions
1. endpoint와 status code를 고정한다.
2. request/response 예시를 포함한다.
3. frontend와 test agent가 재사용할 수 있게 정리한다.

## Format
1. 작업 요약
2. endpoint 목록
3. request/response 예시
4. validation 포인트
`,
  tasks: `---
id: sample-service-test
type: test
version: 1.3.0
owner_agent: test
status: draft
depends_on: [api]
---

# 목적
sample-service CRUD runtime이 contract대로 동작하는지 검증하는 test 시나리오를 정의한다.

# 입력
## 검증 대상
- backend API
- generated frontend flow
- ai-server health 및 generated context

## 핵심 테스트
1. task 생성 성공
2. task 목록 조회 성공
3. task detail 조회 성공
4. status 변경 성공과 validation 실패
5. 삭제 성공 후 재조회 404

# 출력
- automated test 기준
- manual smoke test 체크리스트
- runtime 확인 evidence 포인트

# 실행 규칙
1. success와 failure case를 모두 포함한다.
2. CRUD 전체 흐름을 검증한다.
3. runtime 확인 절차를 문서화한다.

# Validation 기준
- 400, 404, 204 케이스가 포함되어야 한다.
- frontend manual smoke가 포함되어야 한다.
- generated runtime 확인 절차가 있어야 한다.

# Prompt
## Role
당신은 Test Agent다. sample-service runtime 검증 시나리오를 만든다.

## Instructions
1. CRUD 전체 흐름을 다룬다.
2. validation과 not-found 케이스를 포함한다.
3. manual smoke test를 함께 정리한다.

## Format
1. 작업 요약
2. test 목록
3. coverage 체크포인트
4. runtime 확인 절차
`,
  review: `---
id: sample-service-review
type: review
version: 1.3.0
owner_agent: review
status: draft
depends_on: [api, test]
---

# 목적
sample-service generated 결과가 reference sample로 충분한지 review 기준을 정의한다.

# 입력
## review 관점
- contract 일치 여부
- runtime 실행 가능 여부
- 문서와 실제 동작의 정합성
- validation 메시지의 가독성

## blocker 예시
- CRUD가 끝까지 동작하지 않음
- contract와 구현이 불일치함
- runtime 실행 절차가 문서와 다름

# 출력
- blocker / major / minor 기준
- release readiness 판단 기준

# 실행 규칙
1. 실행 가능성을 미관보다 우선한다.
2. spec, code, docs drift를 반드시 지적한다.
3. 사람이 따라 할 수 있는 runbook이 있어야 한다.

# Validation 기준
- blocker 기준이 있어야 한다.
- runtime 확인 항목이 있어야 한다.
- docs 정합성 검토가 포함되어야 한다.

# Prompt
## Role
당신은 Review Agent다. sample-service를 reference sample 관점에서 검토한다.

## Instructions
1. blocker, major, minor를 구분한다.
2. spec과 generated output의 drift를 찾는다.
3. runtime 확인 절차의 정확성을 본다.

## Format
1. overall verdict
2. blocker
3. major
4. minor
5. required patch directions
`,
  plan: `---
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
1. plan.md는 orchestration의 source of truth다.
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
`,
} as const;

export const defaultSpecs = DEFAULT_DOCS;
