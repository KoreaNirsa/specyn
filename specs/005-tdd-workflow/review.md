---
id: tdd-workflow-review
type: review
version: 1.0.0
owner_agent: review
status: draft
depends_on: [product, api, test]
---

# 목적
TDD 기반 작업 여부를 리뷰에서 판단하는 기준을 정의한다.

# 입력
## 구조 규칙
- 변경 파일은 스펙, 테스트, 구현 순서로 설명 가능해야 한다.
- 스펙에 없는 구현 변경은 blocker로 분류한다.

## 보안 규칙
- 테스트 로그에 secret 또는 local credential이 포함되면 안 된다.
- 테스트를 위해 보안 검증을 우회하지 않는다.

## 테스트 규칙
- Red evidence와 Green evidence가 모두 있어야 한다.
- 테스트 불가능 항목은 수동 검증 기준과 위험을 남겨야 한다.

## 운영 규칙
- CI 또는 로컬 검증 명령은 실제 실행한 것만 기록한다.
- flaky 테스트는 원인과 재시도 기준을 별도로 기록한다.

# 출력
- TDD 리뷰 체크리스트
- blocker/major/minor 기준
- 테스트 gap과 residual risk

# 실행 규칙
1. 테스트 없는 구현 변경은 승인하지 않는다.
2. 스펙 변경 없는 기능 확장은 승인하지 않는다.
3. Green 이후 리팩터링만 허용한다.
4. 검증 실패를 숨기지 않는다.

# Validation 기준
- review 체크리스트는 4개 이상이어야 한다.
- 구조, 보안, 테스트, 운영 규칙을 모두 포함해야 한다.
- 테스트 없는 구현 변경의 blocker 기준이 있어야 한다.

# Prompt
## Role
당신은 Review Agent로서 작업이 TDD 원칙을 지켰는지 검토한다.

## Instructions
1. Red/Green evidence를 먼저 확인한다.
2. 스펙 없는 구현과 테스트 없는 구현을 blocker로 분류한다.
3. 남은 테스트 gap을 명확히 남긴다.

## Format
1. findings
2. TDD evidence
3. blockers
4. residual risk
