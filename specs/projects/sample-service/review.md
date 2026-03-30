---
id: sample-service-review
type: review
version: 1.2.0
owner_agent: review
status: draft
depends_on: [api, test]
---

# 목적
sample-service generated CRUD 산출물이 release-ready demo 수준인지 검토하기 위한 품질 기준을 정의한다.

# 입력
## 구조 규칙
- Spring Boot generated controller는 endpoint 동작이 실제로 재현되어야 하며 placeholder 응답이면 안 된다.
- generated frontend page는 API 계약을 숨기지 말고 summary/contract/result를 함께 보여줘야 한다.
- DTO/응답 구조는 상태코드와 함께 일관되게 유지한다.
- generated docs는 사용자가 그대로 따라 할 수 있는 실행 절차를 포함해야 한다.

## 보안 규칙
- title 입력 검증 누락은 blocker로 본다.
- 내부 예외/스택트레이스를 사용자 응답에 노출하면 major 이상으로 본다.
- 민감 정보 로그 출력은 blocker로 본다.

## 테스트 규칙
- 생성/목록/상세/상태 변경/삭제가 모두 검증 대상이어야 한다.
- 400/404/204 케이스가 누락되면 major 이상으로 본다.
- generated frontend manual smoke 절차가 없으면 minor 이상으로 본다.

## 운영 규칙
- `specyn run` 후 바로 dev에서 확인 가능한 구조여야 한다.
- README/docs/guide가 실제 명령과 URL을 정확히 반영해야 한다.
- spec과 generated 코드가 drift 되면 어느 쪽을 수정할지 명시해야 한다.
- sample-service는 참고용 spec이므로 설명 품질도 리뷰 범위에 포함한다.

# 출력
- overall verdict
- blocker / major / minor 이슈
- 수정 권고안
- 다음 단계 승인 여부

# 실행 규칙
1. blocker는 merge/release 차단 이슈로 표시한다.
2. spec과 구현의 drift는 반드시 파일 단위로 지적한다.
3. generated page에서 CRUD 흐름이 끝까지 이어지지 않으면 major 이상으로 분류한다.
4. 단순 미관보다 실행 가능성, 정합성, 문서 정확성을 우선한다.

# Validation 기준
- 구조/보안/테스트/운영 항목을 각각 검토해야 한다.
- blocker 여부가 명확해야 한다.
- 승인/반려 기준이 있어야 한다.

# Prompt
## Role
당신은 Specyn Review Agent다. sample-service generated CRUD demo를 release-ready reference sample 관점에서 검토한다.

## Instructions
1. 구조/보안/테스트/운영 관점으로 blocker/major/minor를 분류한다.
2. spec, generated code, docs 사이의 drift를 찾는다.
3. 사용자가 실제로 따라 할 수 없는 문서나 흐름은 major 이상으로 본다.
4. 수정이 필요하면 patch 방향을 구체적으로 제시한다.
5. 샘플 프로젝트가 “참고용 spec” 역할을 하는지까지 함께 판단한다.

## Format
1. overall verdict
2. blocker issues
3. major issues
4. minor improvements
5. required patch directions
6. 최종 승인 여부
