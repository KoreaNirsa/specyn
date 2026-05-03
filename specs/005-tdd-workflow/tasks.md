---
id: tdd-workflow-test
type: test
version: 1.0.0
owner_agent: test
status: draft
depends_on: [api, product]
---

# 목적
모든 향후 작업이 TDD 순서를 따르는지 검증하는 테스트 기준을 정의한다.

# 입력
## 시나리오
- 구현 변경 전에 실패 테스트 또는 실패 검증 기준이 기록된다.
- 구현 후 같은 테스트 명령이 통과한다.
- 테스트 없이 구현된 변경은 review에서 blocker로 표시된다.
- 테스트 불가능 항목은 스펙에 수동 검증 기준과 보류 사유가 남는다.
- 리팩터링은 Green 이후에만 수행된다.

# 출력
- TDD 검증 시나리오
- Red/Green/Refactor evidence 요구사항
- 테스트 gap 처리 기준

# 실행 규칙
1. 새 기능은 실패 테스트를 먼저 만든다.
2. 버그 수정은 재현 테스트를 먼저 만든다.
3. 문서/스펙 변경은 링크, 경로, validator 테스트를 먼저 확인한다.
4. 테스트 불가능 사유는 final response와 PR 설명에 남긴다.

# Validation 기준
- 테스트 시나리오는 4개 이상이어야 한다.
- Red와 Green evidence 기준이 포함되어야 한다.
- 테스트 불가능 항목의 대체 검증 기준이 포함되어야 한다.

# Prompt
## Role
당신은 Test Agent로서 모든 작업의 TDD evidence를 검증한다.

## Instructions
1. 실패 테스트 없이 구현이 시작되지 않도록 한다.
2. 구현 후 같은 검증 명령을 다시 실행한다.
3. 테스트 gap을 숨기지 않는다.

## Format
1. red evidence
2. green evidence
3. refactor notes
4. gaps
