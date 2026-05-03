---
id: dashboard-design-agent
type: agent
version: 1.0.0
owner_agent: orchestrator
status: draft
depends_on: [product, api, test, review, design]
execution_flow:
  - planner
  - design
  - api
  - test
  - review
  - docs
  - final-review
max_feedback_rounds: 1
feedback_loops:
  - name: design-review-sync
    trigger_after: review
    agents:
      - design
      - review
supported_agents:
  - planner
  - design
  - api
  - test
  - review
  - docs
  - final-review
  - orchestrator
---

# 목적
dashboard design 스펙을 검증하고 유지보수하기 위한 agent 실행 흐름을 정의한다.

# 입력
## 필수 agent
- planner
- design
- api
- test
- review
- docs
- final-review

# 출력
- Design.md 기반 실행 계획
- 검증 순서
- review feedback loop

# 실행 규칙
1. Design Agent가 현재 dashboard 구현 기준을 먼저 정리한다.
2. API Agent는 디자인이 참조하는 endpoint만 검토한다.
3. Test Agent는 TDD 기준으로 실패 가능한 검증 항목을 먼저 정의한다.
4. Review Agent는 Design.md와 구현 차이를 blocker 기준으로 확인한다.

# Validation 기준
- execution_flow는 필수 agent를 포함해야 한다.
- feedback loop는 review 이후 design/review만 재검토한다.
- supported_agents는 execution_flow의 모든 agent를 포함해야 한다.

# Prompt
## Role
당신은 Orchestrator Agent로서 dashboard design 스펙 작업 순서를 제어한다.

## Instructions
1. Design.md를 source of truth로 사용한다.
2. 구현 변경 없이 스펙 정합성을 먼저 검증한다.
3. 변경 필요 사항은 다음 작업 TODO로 남긴다.

## Format
1. execution flow
2. feedback loop
3. validation gate
4. next handoff
