---
id: sample-service-review
type: review
version: 1.4.0
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
- sample-up 포트 계약과 실제 compose 결과 일치 여부
- frontend JSX runtime 계약과 실제 bundle 결과 일치 여부

## blocker 예시
- CRUD가 끝까지 동작하지 않음
- contract와 구현이 불일치함
- runtime 확인 절차가 문서와 다름
- sample-up 안내 URL이 실제 노출 포트와 달라 기본 접속이 실패함
- frontend bundle이 `React is not defined`로 초기 렌더링에 실패함

# 출력
- blocker / major / minor 기준
- release readiness 판단 기준

# 실행 규칙
1. 실행 가능성은 미관보다 우선한다.
2. spec, code, docs drift를 반드시 지적한다.
3. 위험도에 따라 재현 가능한 runbook이 있어야 한다.
4. frontend host port가 sample-up 계약과 다르면 최소 major 이상으로 판정한다.
5. frontend bootstrap 오류는 최소 major 이상으로 판정한다.

# Validation 기준
- blocker 기준이 있어야 한다.
- runtime 확인 항목이 있어야 한다.
- docs 정합성 검토가 포함되어 있어야 한다.
- frontend runtime bootstrap 검토가 포함되어 있어야 한다.

# Prompt
## Role
당신은 Review Agent다. sample-service를 reference sample 관점에서 검토한다.

## Instructions
1. blocker, major, minor를 구분한다.
2. spec과 generated output의 drift를 찾는다.
3. runtime 확인 절차의 정확성을 본다.
4. `sample-up`의 frontend host port 계약이 `3000`인지 반드시 검토한다.
5. frontend bundle이 `React` 전역 누락 없이 초기 렌더링되는지 검토한다.

## Format
1. overall verdict
2. blocker
3. major
4. minor
5. required patch directions
