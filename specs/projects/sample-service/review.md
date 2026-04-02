---
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
