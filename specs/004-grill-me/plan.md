---
id: grill-me-agent
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
max_feedback_rounds: 2
feedback_loops:
  - name: grill-me-spec-hardening
    trigger_after: review
    agents:
      - planner
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
Grill Me 절차를 Specyn 작업 흐름에 끼워 넣는 agent 실행 순서를 정의한다.

# 입력
## 필수 agent
- planner
- api
- test
- review
- docs
- final-review

# 출력
- Grill Me 질문 생성 및 검토 순서
- 미해결 질문 handoff
- final-review 승인 gate

# 실행 규칙
1. Planner가 질문 대상을 정리한다.
2. Review Agent가 Grill Me 질문을 생성하고 severity를 부여한다.
3. Test Agent가 blocker 질문을 검증 gate로 연결한다.
4. Final Review는 unresolved blocker가 없을 때만 승인한다.

# Validation 기준
- execution_flow는 필수 agent를 포함해야 한다.
- feedback loop는 planner/review 사이에서만 Grill Me 보완을 반복한다.
- max_feedback_rounds는 2를 초과하지 않는다.

# Prompt
## Role
당신은 Orchestrator Agent로서 Grill Me 적용 순서를 제어한다.

## Instructions
1. 구현 전 질문과 답변을 먼저 정리한다.
2. unresolved blocker를 구현 단계로 넘기지 않는다.
3. 질문 결과를 docs/final-review handoff에 남긴다.

## Format
1. execution flow
2. question gate
3. blocker handling
4. next handoff
