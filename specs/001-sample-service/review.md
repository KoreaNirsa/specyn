---
id: sample-service-review
type: review
version: 1.4.2
owner_agent: review
status: draft
depends_on: [api, test]
---

# 목적
sample-service generated 결과가 reference sample로 적합한지 review 기준을 정의한다.

# 입력
## 구조 규칙
- backend는 `global / common / domain` 계층을 유지해야 한다.
- Controller는 비즈니스 로직을 직접 담지 않고 application 계층을 호출해야 한다.
- DTO와 domain 모델은 역할이 분리되어야 한다.
- 공통 예외 응답 구조는 모든 실패 케이스에서 일관돼야 한다.

## 보안 규칙
- 입력 검증 누락은 blocker로 분류한다.
- 민감 정보 로그 노출은 blocker로 분류한다.
- 내부 구현 세부 정보를 외부 오류 메시지로 그대로 노출하면 major로 분류한다.
- 인증이 없는 로컬 샘플이라도 허용 상태값 검증은 반드시 유지해야 한다.

## 테스트 규칙
- 주요 성공 시나리오와 실패 시나리오가 모두 존재해야 한다.
- 400, 404, 204 케이스가 테스트 또는 수동 검증 체크리스트에 포함돼야 한다.
- frontend smoke에서 첫 화면 로드와 task 생성 흐름이 확인돼야 한다.
- flaky test 가능성이 있으면 수정 방향을 리뷰에 남겨야 한다.

## 운영 규칙
- `sample-up` 포트 계약은 frontend `5173`, backend `8080`, ai-server `8000`과 일치해야 한다.
- 문서, compose, generated runtime 사이에 drift가 있으면 major 이상으로 분류한다.
- frontend bundle은 `React is not defined` 없이 초기 렌더링되어야 한다.
- 실행 절차는 runbook만 보고 재현 가능해야 한다.

# 출력
- overall verdict
- blocker / major / minor 기준
- release readiness 판단 기준

# 실행 규칙
1. blocker는 merge 차단 사유로 명시한다.
2. 리뷰 결과는 파일 또는 실행 흐름 단위로 추적 가능해야 한다.
3. spec과 구현이 어긋나면 어느 쪽을 수정해야 하는지 방향을 적는다.

# Validation 기준
- review 체크리스트는 4개 이상 명시해야 한다.
- 구조, 보안, 테스트, 운영 관점이 모두 포함돼야 한다.

# Prompt
## Role
당신은 Review Agent로서 sample-service를 reference sample 관점에서 검토한다.

## Instructions
1. blocker, major, minor를 구분한다.
2. spec과 generated output의 drift를 찾는다.
3. runtime 확인 결과를 release readiness 판단에 반영한다.

## Format
1. overall verdict
2. blocker
3. major
4. minor
5. required patch directions
