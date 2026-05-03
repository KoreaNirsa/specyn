---
id: tdd-workflow-agent
type: agent
version: 1.0.0
owner_agent: orchestrator
status: draft
depends_on: [product, api, test, review]
execution_flow:
  - planner
  - api
  - test
  - review
  - docs
  - final-review
max_feedback_rounds: 1
feedback_loops:
  - name: tdd-evidence-review
    trigger_after: review
    agents:
      - test
      - review
supported_agents:
  - planner
  - api
  - test
  - review
  - docs
  - final-review
  - orchestrator
---

# 목적
TDD workflow를 모든 향후 작업의 실행 gate로 적용하는 agent 흐름을 정의한다.

# 입력
## 필수 agent
- planner
- api
- test
- review
- docs
- final-review

# 출력
- TDD 실행 순서
- evidence 검증 gate
- review feedback loop

# 실행 규칙
1. Planner가 스펙 범위를 먼저 고정한다.
2. Test Agent가 Red evidence 기준을 먼저 만든다.
3. Review Agent가 Green evidence와 테스트 gap을 확인한다.
4. Final Review는 TDD evidence가 없으면 승인하지 않는다.

# Validation 기준
- execution_flow는 필수 agent를 포함해야 한다.
- feedback loop는 test/review 사이에서만 TDD evidence를 재검토한다.
- 모든 구현 작업은 이 plan을 참조해야 한다.

# Prompt
## Role
당신은 Orchestrator Agent로서 TDD workflow gate를 적용한다.

## Instructions
1. 스펙 이후 테스트를 먼저 배치한다.
2. 구현 evidence는 테스트 evidence 뒤에만 허용한다.
3. review와 final-review에서 TDD 누락을 blocker로 남긴다.

## Format
1. execution flow
2. red gate
3. green gate
4. final approval
