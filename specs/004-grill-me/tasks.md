---
id: grill-me-test
type: test
version: 1.0.0
owner_agent: test
status: draft
depends_on: [api, product]
---

# 목적
Grill Me 절차가 스펙 검증 단계에서 누락되지 않도록 테스트 기준을 정의한다.

# 입력
## 시나리오
- 새 feature 스펙에는 Grill Me 질문 또는 미수행 사유가 존재해야 한다.
- blocker 질문이 unresolved이면 구현 단계로 넘어가지 않는다.
- 질문은 목적, 입력, 출력, 실행 규칙, Validation 기준 중 하나에 연결되어야 한다.
- resolved와 unresolved가 같은 항목을 중복 포함하지 않는다.
- final-review는 unresolved blocker가 없을 때만 승인한다.

# 출력
- Grill Me 절차 검증 기준
- blocker 처리 기준
- final-review 승인 조건

# 실행 규칙
1. Grill Me 테스트는 구현 테스트보다 먼저 작성한다.
2. 실패하는 질문 검증을 확인한 뒤 스펙을 보완한다.
3. unresolved blocker는 테스트 실패로 취급한다.
4. 질문이 없는 경우에는 명시적 예외 사유가 있어야 한다.

# Validation 기준
- 테스트 시나리오는 4개 이상이어야 한다.
- unresolved blocker 처리 기준이 있어야 한다.
- final-review 승인 조건이 있어야 한다.

# Prompt
## Role
당신은 Test Agent로서 Grill Me 절차의 누락을 테스트로 막는다.

## Instructions
1. 질문 존재 여부와 blocker 상태를 검증한다.
2. 스펙 섹션 연결 여부를 확인한다.
3. unresolved blocker가 있으면 실패로 보고한다.

## Format
1. test scenarios
2. blocker checks
3. approval gate
4. gaps
