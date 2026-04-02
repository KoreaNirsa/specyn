---
id: sample-service-api
type: api
version: 1.3.0
owner_agent: api
status: draft
depends_on: [product]
---

# 목적
sample-service CRUD 기능에 필요한 API contract를 정의한다.

# 입력
## API 목록
- GET /api/v1/tasks
- GET /api/v1/tasks/{id}
- POST /api/v1/tasks
- PATCH /api/v1/tasks/{id}/status
- DELETE /api/v1/tasks/{id}

## 제약
- title은 required다.
- status는 PENDING, DONE만 허용한다.
- not found는 404를 사용한다.

# 출력
- request/response 구조
- status code 정책
- error response 규칙

# 실행 규칙
1. API contract는 generated frontend와 backend가 함께 사용한다.
2. placeholder endpoint를 남기지 않는다.
3. error payload는 code, message, path, timestamp를 포함한다.

# Validation 기준
- 모든 endpoint가 정의되어 있어야 한다.
- success와 failure case가 있어야 한다.
- status와 payload 구조가 일관돼야 한다.

# Prompt
## Role
당신은 API Agent다. sample-service CRUD API contract를 정리한다.

## Instructions
1. endpoint와 status code를 고정한다.
2. request/response 예시를 포함한다.
3. frontend와 test agent가 재사용할 수 있게 정리한다.

## Format
1. 작업 요약
2. endpoint 목록
3. request/response 예시
4. validation 포인트
