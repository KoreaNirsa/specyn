---
id: sample-service-test
type: test
version: 1.2.0
owner_agent: test
status: draft
depends_on: [api]
---

# 목적
sample-service generated CRUD 구현이 제품 요구사항과 API 계약을 만족하는지 검증할 테스트 시나리오를 정의한다.

# 입력
## 테스트 범위
- generated backend controller API 테스트
- 상태 전환 및 오류 응답 테스트
- generated ai-server route smoke test
- generated frontend manual smoke checklist

## 시나리오
1. POST /api/v1/tasks 요청 시 201과 생성된 Task payload를 반환한다.
2. GET /api/v1/tasks 요청 시 seeded task와 신규 task를 포함한 목록을 반환한다.
3. GET /api/v1/tasks/{id} 에서 존재하지 않는 ID 조회 시 404를 반환한다.
4. PATCH /api/v1/tasks/{id}/status 에서 잘못된 status 값 입력 시 400을 반환한다.
5. PATCH /api/v1/tasks/{id}/status 성공 시 상태가 `DONE` 또는 `PENDING` 으로 갱신된다.
6. DELETE /api/v1/tasks/{id} 성공 후 재조회 시 404를 확인한다.
7. generated frontend page는 생성/상세 조회/상태 변경/삭제를 모두 재현할 수 있어야 한다.

## 테스트 대상
- Backend generated controller
- 오류 응답 payload
- AI Server generated context route
- Frontend generated project page의 핵심 사용자 흐름

# 출력
- API 테스트 코드 또는 smoke test 시나리오
- endpoint coverage 체크리스트
- 수동 QA가 필요한 generated UI 확인 포인트
- 실패 시 수정이 필요한 구현 포인트

# 실행 규칙
1. 모든 endpoint를 최소 1회 이상 검증한다.
2. 성공/실패 시나리오를 모두 포함한다.
3. 상태코드와 응답 본문을 함께 검증한다.
4. 삭제 성공 후에는 204와 이후 404 재조회를 함께 본다.
5. flaky test를 만들지 않는다.

# Validation 기준
- endpoint coverage 100%
- 400/404/204 핵심 케이스 포함
- 정상/실패 시나리오 모두 존재
- frontend manual smoke test 포인트가 문서화되어 있어야 한다.

# Prompt
## Role
당신은 Specyn Test Agent다. sample-service generated CRUD 흐름이 계약대로 동작하는지 검증하는 테스트를 설계한다.

## Instructions
1. 생성/목록/상세/상태 변경/삭제를 모두 다룬다.
2. validation, not-found, success 케이스를 분리한다.
3. generated frontend page에서 수동으로 확인할 UX 흐름도 함께 정리한다.
4. Review Agent가 바로 사용할 coverage와 리스크를 남긴다.
5. CI에 올리기 쉬운 deterministic 시나리오를 우선한다.

## Format
1. 작업 요약
2. 생성/수정된 테스트 파일 목록
3. endpoint coverage 체크리스트
4. validation 결과
5. Review Agent 전달사항
