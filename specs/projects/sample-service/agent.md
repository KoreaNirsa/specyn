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
이 문서는 sample-service에서 어떤 Agent가 어떤 순서와 책임으로 참여하는지 정의한다.

# 입력
## Agent 카탈로그
- Planner Agent: 제품 목표와 acceptance criteria 정규화
- Design Agent: generated page UX/상태 전이 정리
- API Agent: Task CRUD 계약 고정
- Backend Agent: generated Spring Boot CRUD controller 구현
- Frontend Agent: generated CRUD 페이지 구현
- DBA Agent: 샘플 DB 스키마/저장 전략 정리
- DevOps Agent: dev 실행, compose, 환경 변수 계약 정리
- Test Agent: generated API/UI smoke 테스트 정리
- Code Analysis Agent: generated 코드 구조 리스크 점검
- Security Agent: 입력 검증, 오류 응답, 로그 정책 점검
- Performance Agent: 로컬 CRUD 경로의 병목과 관측 포인트 점검
- Review Agent: 샘플 프로젝트 완성도 검토
- Docs Agent: README/docs/guide/playbook 정리
- Final Review Agent: sample-service를 reference sample로 승인할지 결정
- RAG Agent(optional): 내부 문서 검색 보조
- Orchestrator Agent: 전체 흐름 제어

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
- `execution_flow`는 기본 실행 순서를 의미한다.
- `feedback_loops`는 계약/UX/문서 drift를 줄이기 위한 bounded loop다.
- `max_feedback_rounds: 2` 이므로 각 loop는 최대 2개의 feedback round까지 재진입할 수 있다.
- blocker 해소, 문서 drift 수정, 계약 불일치 정정 같은 명확한 이유가 있을 때만 재실행한다.
- 각 round는 `UNRESOLVED`, `BLOCKERS`, `NEXT_HANDOFF`를 남기며 다음 Agent와 계속 조정한다.

## 실패 처리 정책
- validation 실패 시 다음 단계로 진행하지 않는다.
- generated CRUD 흐름이 끝까지 동작하지 않으면 Final Review 이전에 중단할 수 있다.
- destructive change는 rollback 또는 workspace 분리 전략 없이 승인하지 않는다.
- 같은 이슈가 feedback round 이후에도 남아 있으면 human review로 승격한다.

# 출력
- ordered execution flow
- feedback loop plan
- validation ownership matrix
- retry / stop 정책
- 단계별 handoff 요약

# 실행 규칙
1. `agent.md`가 sample-service의 source of truth다.
2. 필수 agent(planner/api/test/review/docs/final-review)는 반드시 포함한다.
3. docs 단계에서는 run 명령, 옵션, 확인 URL이 실제 구현과 일치해야 한다.
4. Final Review는 “참고 가능한 spec인지”와 “실행 가능한 CRUD demo인지”를 함께 본다.
5. 같은 Agent 재진입 시에는 변경 이유와 해결된 drift를 남긴다.
6. feedback round는 품질 게이트가 통과되거나 `max_feedback_rounds`를 모두 사용할 때까지 계속 진행한다.

# trace / handoff contract
- 각 Agent 결과는 `STEP_LABEL`, `AGENT`, `PHASE`, `FEEDBACK_ROUND`, `STATUS`를 남긴다.
- `CHANGED_FILES`, `RESOLVED`, `UNRESOLVED`, `BLOCKERS`, `NEXT_HANDOFF`를 구조적으로 기록한다.
- feedback round에서는 직전 round 대비 변경점과 미해결 이슈만 요약한다.
- 향후 dashboard / trace / run history 기능을 고려해 사람이 읽기 쉬운 구조를 유지한다.

# Validation 기준
- 필수 agent가 execution_flow에 포함되어야 한다.
- feedback loop는 상한(max_feedback_rounds 또는 max_rounds)을 가져야 한다.
- supported_agents와 execution_flow, feedback_loops가 서로 정합해야 한다.
- 실패 시 stop/retry 조건이 명시되어야 한다.
- docs/guide 정합성 검토 책임이 포함되어야 한다.

# Prompt
## Role
당신은 Specyn Orchestrator Agent다. sample-service CRUD demo를 완성하기 위한 실행 그래프와 validation ownership을 설계한다.

## Instructions
1. sample-service의 execution flow와 bounded feedback loop를 정리한다.
2. 어떤 Agent가 어떤 산출물을 책임지는지 명확히 적는다.
3. spec → generated code → docs 간 drift를 줄이기 위한 handoff를 강조한다.
4. retry 가능한 오류와 즉시 stop 해야 하는 blocker를 구분한다.
5. 결과를 실제 `specyn run` 흐름에 바로 사용할 수 있도록 구조화한다.

## Format
1. ordered execution flow
2. feedback loop plan
3. validation ownership matrix
4. retry policy
5. stop / rollback policy
6. 단계별 handoff 요약
