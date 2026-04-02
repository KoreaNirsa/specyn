---
id: sample-service-test
type: test
version: 1.4.1
owner_agent: test
status: draft
depends_on: [api]
---

# 목적
sample-service CRUD runtime이 contract대로 동작하는지 검증할 테스트 시나리오를 정의한다.

# 입력
## 테스트 범위
- backend API
- generated frontend flow
- ai-server health 및 generated context
- `sample-up` 포트 계약: frontend `3000`, backend `8080`, ai-server `8000`
- frontend bootstrap 오류 여부

## 시나리오
- `POST /api/v1/tasks`로 유효한 제목을 보내 task 생성에 성공한다.
- `GET /api/v1/tasks`와 `GET /api/v1/tasks/{id}`로 생성된 task 조회에 성공한다.
- `PATCH /api/v1/tasks/{id}/status`로 `DONE` 상태 변경에 성공한다.
- 허용되지 않은 상태값으로 상태 변경을 시도하면 400을 반환한다.
- `DELETE /api/v1/tasks/{id}`는 204를 반환하고 이후 상세 조회는 404를 반환한다.
- frontend 첫 화면 로드 시 `React is not defined` 또는 import 누락 오류가 없어야 한다.

## 테스트 대상

- Controller 또는 Route Layer
- Service / Use Case
- Exception Handler
- 주요 사용자 흐름

# 출력

- automated test 기준
- manual smoke test 체크리스트
- runtime 확인 evidence 수집 포인트

# 실행 규칙
1. success와 failure case를 모두 포함한다.
2. CRUD 전체 흐름을 검증한다.
3. HTTP 상태코드와 응답 본문을 함께 확인한다.
4. frontend smoke는 `http://localhost:3000` 기준으로 검증한다.

# Validation 기준
- 테스트 시나리오는 4개 이상이어야 한다.
- 400, 404, 204 케이스가 포함되어야 한다.
- frontend manual smoke가 포함되어야 한다.

# Prompt
## Role
당신은 Test Agent로서 sample-service runtime 검증 시나리오를 만든다.

## Instructions
1. CRUD 전체 흐름을 빠짐없이 다룬다.
2. validation과 not-found 케이스를 포함한다.
3. manual smoke test를 명확히 정리한다.

## Format
1. 작업 요약
2. test 목록
3. coverage 체크사항
4. runtime 확인 evidence
