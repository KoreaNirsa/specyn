STEP_LABEL: api-contract-v1
AGENT: api
PHASE: base
FEEDBACK_ROUND: 0
STATUS: done
CHANGED_FILES:
- api-contract.md
RESOLVED:
- CRUD endpoint 5종의 HTTP contract를 고정했다.
- request/response/error payload 구조를 deterministic하게 정의했다.
- Backend/Frontend/Test/Docs 재사용을 위한 공통 contract 표를 제공했다.
UNRESOLVED:
- 없음
BLOCKERS:
- 없음
NEXT_HANDOFF:
- Backend Agent는 본 문서의 endpoint/status code/error code를 구현과 테스트 fixture의 단일 기준으로 사용한다.
- Frontend/Test/Docs Agent는 "Agent Reuse Contract Table"과 "Validation Matrix"를 그대로 재사용한다.

# 작업 요약
`api.md`(v1.3.0) 기준으로 task CRUD API를 OpenAPI 친화적으로 정제했다. 본 계약은 `sample-service`의 backend/frontend/test/docs가 공유하는 단일 기준 문서다.

ASSUMPTION:
- `taskId`는 path parameter에서 문자열 UUID 형식을 사용한다.
- Task 리소스 필드는 스펙 최소 요구사항만 포함하여 `id`, `title`, `status`로 고정한다.
- validation 실패 응답은 `400 Bad Request`로 통일한다.

# 도메인 및 공통 스키마
## Enum
- `TaskStatus`: `PENDING` | `DONE`

## Object: Task
- `id` (string, uuid, required)
- `title` (string, required, minLength: 1, maxLength: 200)
- `status` (`TaskStatus`, required)

## Object: ErrorResponse
- `code` (string, required)
- `message` (string, required, human-readable)
- `path` (string, required, request path)
- `timestamp` (string, required, RFC 3339 date-time)

## Error Code Set (Deterministic)
- `VALIDATION_ERROR` (`400`)
- `TASK_NOT_FOUND` (`404`)
- `INTERNAL_SERVER_ERROR` (`500`)

# Endpoint Contract
## 1) GET /api/v1/tasks
- Description: task 목록 조회
- Success:
  - `200 OK`
  - Response Body:
    - `items` (array of `Task`, required)
- Failure:
  - `500 Internal Server Error` + `ErrorResponse`

Example Response `200`:
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Write API contract",
      "status": "PENDING"
    }
  ]
}
```

## 2) GET /api/v1/tasks/{id}
- Description: task 상세 조회
- Path Param:
  - `id` (string, uuid, required)
- Success:
  - `200 OK`
  - Response Body: `Task`
- Failure:
  - `404 Not Found` + `TASK_NOT_FOUND`
  - `400 Bad Request` + `VALIDATION_ERROR` (id format invalid)
  - `500 Internal Server Error` + `INTERNAL_SERVER_ERROR`

Example Response `200`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Write API contract",
  "status": "PENDING"
}
```

## 3) POST /api/v1/tasks
- Description: task 생성
- Request Body:
  - `title` (string, required, minLength: 1, maxLength: 200)
- Success:
  - `201 Created`
  - Response Body: `Task` (status 기본값 `PENDING`)
- Failure:
  - `400 Bad Request` + `VALIDATION_ERROR`
  - `500 Internal Server Error` + `INTERNAL_SERVER_ERROR`

Example Request:
```json
{
  "title": "Write API contract"
}
```

Example Response `201`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Write API contract",
  "status": "PENDING"
}
```

## 4) PATCH /api/v1/tasks/{id}/status
- Description: task status 변경
- Path Param:
  - `id` (string, uuid, required)
- Request Body:
  - `status` (`TaskStatus`, required)
- Success:
  - `200 OK`
  - Response Body: `Task`
- Failure:
  - `400 Bad Request` + `VALIDATION_ERROR` (invalid enum / missing field / invalid id)
  - `404 Not Found` + `TASK_NOT_FOUND`
  - `500 Internal Server Error` + `INTERNAL_SERVER_ERROR`

Example Request:
```json
{
  "status": "DONE"
}
```

Example Response `200`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Write API contract",
  "status": "DONE"
}
```

## 5) DELETE /api/v1/tasks/{id}
- Description: task 삭제
- Path Param:
  - `id` (string, uuid, required)
- Success:
  - `204 No Content`
- Failure:
  - `400 Bad Request` + `VALIDATION_ERROR` (invalid id)
  - `404 Not Found` + `TASK_NOT_FOUND`
  - `500 Internal Server Error` + `INTERNAL_SERVER_ERROR`

# 표준 오류 응답 예시
Example Response `400`:
```json
{
  "code": "VALIDATION_ERROR",
  "message": "status must be one of [PENDING, DONE]",
  "path": "/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/status",
  "timestamp": "2026-04-01T14:20:00Z"
}
```

Example Response `404`:
```json
{
  "code": "TASK_NOT_FOUND",
  "message": "Task not found: 550e8400-e29b-41d4-a716-446655440000",
  "path": "/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-04-01T14:20:01Z"
}
```

# Agent Reuse Contract Table
| Endpoint | Success | Validation Failure | Not Found | Notes |
|---|---|---|---|---|
| GET /api/v1/tasks | 200 + items[] | - | - | 목록은 항상 `items` key 사용 |
| GET /api/v1/tasks/{id} | 200 + Task | 400 + VALIDATION_ERROR | 404 + TASK_NOT_FOUND | id는 uuid 포맷 검증 |
| POST /api/v1/tasks | 201 + Task | 400 + VALIDATION_ERROR | - | 기본 status는 `PENDING` |
| PATCH /api/v1/tasks/{id}/status | 200 + Task | 400 + VALIDATION_ERROR | 404 + TASK_NOT_FOUND | status enum 엄격 검증 |
| DELETE /api/v1/tasks/{id} | 204 (empty) | 400 + VALIDATION_ERROR | 404 + TASK_NOT_FOUND | 삭제 후 detail 재조회 404 기대 |

# Validation Matrix
- `title`:
  - required
  - string
  - trim 후 빈 문자열 불가
  - maxLength 200
- `status`:
  - required (PATCH)
  - enum only: `PENDING`, `DONE`
- `id` path param:
  - required
  - uuid format

# OpenAPI-Friendly Summary
## Paths
- `/api/v1/tasks`
  - `get`
  - `post`
- `/api/v1/tasks/{id}`
  - `get`
  - `delete`
- `/api/v1/tasks/{id}/status`
  - `patch`

## Components/Schemas
- `Task`
- `CreateTaskRequest`
- `UpdateTaskStatusRequest`
- `TaskListResponse`
- `ErrorResponse`

## Reusable Responses
- `BadRequestError` (`400`)
- `NotFoundError` (`404`)
- `InternalServerError` (`500`)

# Backend Handoff Notes
## Spring Boot 구조 힌트
- `global`
  - 예외 처리: `global/exception/GlobalExceptionHandler`
  - 오류 응답 모델: `global/error/ErrorResponse`
- `common`
  - enum: `common/enums/TaskStatus`
  - 공통 validator: `common/validation/*`
- `domain/task`
  - controller: `domain/task/api/TaskController`
  - request/response DTO: `domain/task/api/dto/*`
  - service: `domain/task/application/TaskService`

## FastAPI 구조 힌트
- `app/global`
  - exception handler, error model
- `app/common`
  - enum, validators
- `app/domain/task`
  - router, schema, service

# Review Agent Drift Checkpoints
- endpoint path drift: `/status` suffix 누락 여부
- status code drift: create가 `201`인지 여부
- delete response drift: `204` + empty body 유지 여부
- error payload drift: `code/message/path/timestamp` 누락 여부
- enum drift: `PENDING|DONE` 외 허용 여부

# Validation 결과
- `api.md`의 endpoint 5개 모두 정의됨.
- success/failure 케이스(400/404/204 포함) 모두 정의됨.
- error payload 필수 필드(`code`, `message`, `path`, `timestamp`) 반영됨.
- 계약은 버전 경로(`/api/v1`) 및 에러코드 세트까지 deterministic하게 고정됨.
