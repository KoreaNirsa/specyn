STEP_LABEL: api
AGENT: api
PHASE: feedback
FEEDBACK_ROUND: 2
STATUS: done
CHANGED_FILES:
- /workspace/projects/sample-service/api-handoff.md
RESOLVED:
- CRUD 5개 endpoint의 request/response/error contract를 `api.md`와 현재 구현 기준으로 deterministic 하게 고정했다.
- Spring Boot backend, frontend fetch client, test handoff가 재사용할 wrapper shape와 validation/error 규칙을 명시했다.
- OpenAPI 관점에서 path parameter, request schema, success/error response를 일관된 형태로 정리했다.
UNRESOLVED:
- `500 INTERNAL_ERROR`는 공통 예외 모델로 정의되지만, 실제 runtime evidence는 test/review 단계에서 추가 확인이 필요하다.
- PostgreSQL 기반 end-to-end smoke는 API contract 범위를 넘어가므로 devops/test 단계 확인이 남아 있다.
BLOCKERS:
- none
NEXT_HANDOFF:
- Backend Agent: `/api/v1/tasks` 이하 경로, wrapper shape(`{items,count}`, `{data}`), error code(`VALIDATION_ERROR`, `TASK_NOT_FOUND`, `INTERNAL_ERROR`)를 변경하지 말 것.
- Frontend Agent: `DELETE 204`는 JSON 파싱 없이 성공 처리하고, 실패 시 `error.message`를 사용자 메시지로 사용.
- Test Agent: `400/404/204`와 invalid UUID, missing title, missing status, invalid status enum을 회귀 케이스로 유지.
- Docs/Review Agent: OpenAPI 요약과 실제 구현의 version/path/status/error drift 여부를 우선 점검.

# Work Summary
- Source of truth: `api.md` v1.3.0, `product.md` v1.3.0, 현재 backend/frontend/test 구현.
- Resource: `Task`
- Base path: `/api/v1/tasks`
- Media type: `application/json`

ASSUMPTION:
- `id`는 RFC 4122 UUID 문자열이다.
- `timestamp`, `createdAt`, `updatedAt`는 UTC ISO-8601 `date-time` 문자열이다.

# Endpoint Contract

| Endpoint | Purpose | Request | Success Response | Error Response |
|---|---|---|---|---|
| `GET /api/v1/tasks` | Task 목록 조회 | none | `200 OK` + `TaskListResponse` | `500 Internal Server Error` + `ErrorResponse` |
| `GET /api/v1/tasks/{id}` | Task 상세 조회 | path `id: uuid` | `200 OK` + `TaskResponse` | `400 Bad Request`, `404 Not Found`, `500 Internal Server Error` |
| `POST /api/v1/tasks` | Task 생성 | `CreateTaskRequest` | `201 Created` + `TaskResponse` | `400 Bad Request`, `500 Internal Server Error` |
| `PATCH /api/v1/tasks/{id}/status` | Task 상태 변경 | path `id: uuid` + `UpdateTaskStatusRequest` | `200 OK` + `TaskResponse` | `400 Bad Request`, `404 Not Found`, `500 Internal Server Error` |
| `DELETE /api/v1/tasks/{id}` | Task 삭제 | path `id: uuid` | `204 No Content` + empty body | `400 Bad Request`, `404 Not Found`, `500 Internal Server Error` |

Deterministic status policy:
- `200`: list/detail/update success
- `201`: create success
- `204`: delete success with empty body
- `400`: path/body validation failure
- `404`: task resource not found
- `500`: unexpected server error

# Schema Contract

## Request Models

```yaml
CreateTaskRequest:
  type: object
  required: [title]
  additionalProperties: false
  properties:
    title:
      type: string
      minLength: 1
      maxLength: 200
      description: Required. Blank string is rejected.
    description:
      type: string
      maxLength: 2000
      nullable: true

UpdateTaskStatusRequest:
  type: object
  required: [status]
  additionalProperties: false
  properties:
    status:
      type: string
      enum: [PENDING, DONE]
```

Validation rules:
- `title` is required
- blank `title` returns `400 VALIDATION_ERROR` with message `title is required`
- `title` length over 200 returns `400 VALIDATION_ERROR`
- `description` length over 2000 returns `400 VALIDATION_ERROR`
- missing `status` returns `400 VALIDATION_ERROR` with message `status is required`
- unknown `status` value returns `400 VALIDATION_ERROR` with message `status must be one of [PENDING, DONE]`
- invalid path `id` returns `400 VALIDATION_ERROR` with message `id must be a valid UUID`

## Domain / Response Models

```yaml
Task:
  type: object
  required: [id, title, status, createdAt, updatedAt]
  properties:
    id:
      type: string
      format: uuid
    title:
      type: string
      maxLength: 200
    description:
      type: string
      nullable: true
      maxLength: 2000
    status:
      type: string
      enum: [PENDING, DONE]
    createdAt:
      type: string
      format: date-time
    updatedAt:
      type: string
      format: date-time

TaskListResponse:
  type: object
  required: [items, count]
  properties:
    items:
      type: array
      items:
        $ref: '#/components/schemas/Task'
    count:
      type: integer
      minimum: 0

TaskResponse:
  type: object
  required: [data]
  properties:
    data:
      $ref: '#/components/schemas/Task'
```

Wrapper rules:
- list response shape is always `{ "items": [...], "count": number }`
- detail/create/update response shape is always `{ "data": { ...Task } }`
- delete success returns no JSON body

# Error Contract

```yaml
ErrorResponse:
  type: object
  required: [code, message, path, timestamp]
  properties:
    code:
      type: string
      enum: [VALIDATION_ERROR, TASK_NOT_FOUND, INTERNAL_ERROR]
    message:
      type: string
    path:
      type: string
    timestamp:
      type: string
      format: date-time
```

Error mapping:

| HTTP Status | Code | Trigger | Canonical Message |
|---|---|---|---|
| `400` | `VALIDATION_ERROR` | invalid UUID, missing required field, enum parse failure, malformed JSON | `id must be a valid UUID`, `title is required`, `status is required`, `status must be one of [PENDING, DONE]` |
| `404` | `TASK_NOT_FOUND` | missing task resource | `Task not found: {id}` |
| `500` | `INTERNAL_ERROR` | unhandled exception | `Unexpected server error` |

Readable message rule:
- `message`는 field-focused plain text여야 한다.
- frontend는 `message`를 그대로 표시해도 이해 가능해야 한다.

# Request / Response Examples

## GET /api/v1/tasks

Response `200 OK`

```json
{
  "items": [
    {
      "id": "6d3237ae-570f-4c8c-b3aa-b6d56c87f5c5",
      "title": "Write API contract",
      "description": "Prepare deterministic spec",
      "status": "PENDING",
      "createdAt": "2026-04-07T09:00:00Z",
      "updatedAt": "2026-04-07T09:00:00Z"
    }
  ],
  "count": 1
}
```

## GET /api/v1/tasks/{id}

Response `200 OK`

```json
{
  "data": {
    "id": "6d3237ae-570f-4c8c-b3aa-b6d56c87f5c5",
    "title": "Write API contract",
    "description": "Prepare deterministic spec",
    "status": "PENDING",
    "createdAt": "2026-04-07T09:00:00Z",
    "updatedAt": "2026-04-07T09:00:00Z"
  }
}
```

Response `404 Not Found`

```json
{
  "code": "TASK_NOT_FOUND",
  "message": "Task not found: 6d3237ae-570f-4c8c-b3aa-b6d56c87f5c5",
  "path": "/api/v1/tasks/6d3237ae-570f-4c8c-b3aa-b6d56c87f5c5",
  "timestamp": "2026-04-07T09:10:00Z"
}
```

## POST /api/v1/tasks

Request

```json
{
  "title": "Implement backend",
  "description": "Create REST endpoints"
}
```

Response `201 Created`

```json
{
  "data": {
    "id": "f6dbb4e1-48ac-4d11-88f8-1313f955a9ff",
    "title": "Implement backend",
    "description": "Create REST endpoints",
    "status": "PENDING",
    "createdAt": "2026-04-07T09:20:00Z",
    "updatedAt": "2026-04-07T09:20:00Z"
  }
}
```

Response `400 Bad Request`

```json
{
  "code": "VALIDATION_ERROR",
  "message": "title is required",
  "path": "/api/v1/tasks",
  "timestamp": "2026-04-07T09:21:00Z"
}
```

## PATCH /api/v1/tasks/{id}/status

Request

```json
{
  "status": "DONE"
}
```

Response `200 OK`

```json
{
  "data": {
    "id": "f6dbb4e1-48ac-4d11-88f8-1313f955a9ff",
    "title": "Implement backend",
    "description": "Create REST endpoints",
    "status": "DONE",
    "createdAt": "2026-04-07T09:20:00Z",
    "updatedAt": "2026-04-07T09:31:00Z"
  }
}
```

Response `400 Bad Request`

```json
{
  "code": "VALIDATION_ERROR",
  "message": "status must be one of [PENDING, DONE]",
  "path": "/api/v1/tasks/f6dbb4e1-48ac-4d11-88f8-1313f955a9ff/status",
  "timestamp": "2026-04-07T09:31:30Z"
}
```

## DELETE /api/v1/tasks/{id}

Response `204 No Content`

Empty body.

# OpenAPI-Friendly Summary

```yaml
openapi: 3.0.3
info:
  title: sample-service API
  version: 1.3.0
servers:
  - url: /
paths:
  /api/v1/tasks:
    get:
      operationId: listTasks
      tags: [Tasks]
      responses:
        '200':
          description: Task list
        '500':
          description: Internal server error
    post:
      operationId: createTask
      tags: [Tasks]
      requestBody:
        required: true
      responses:
        '201':
          description: Created
        '400':
          description: Validation error
        '500':
          description: Internal server error
  /api/v1/tasks/{id}:
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: string
          format: uuid
    get:
      operationId: getTask
      tags: [Tasks]
      responses:
        '200':
          description: Task detail
        '400':
          description: Validation error
        '404':
          description: Task not found
        '500':
          description: Internal server error
    delete:
      operationId: deleteTask
      tags: [Tasks]
      responses:
        '204':
          description: Deleted
        '400':
          description: Validation error
        '404':
          description: Task not found
        '500':
          description: Internal server error
  /api/v1/tasks/{id}/status:
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: string
          format: uuid
    patch:
      operationId: updateTaskStatus
      tags: [Tasks]
      requestBody:
        required: true
      responses:
        '200':
          description: Updated
        '400':
          description: Validation error
        '404':
          description: Task not found
        '500':
          description: Internal server error
components:
  schemas:
    Task:
      $ref: '#/components/schemas/Task'
    TaskListResponse:
      $ref: '#/components/schemas/TaskListResponse'
    TaskResponse:
      $ref: '#/components/schemas/TaskResponse'
    ErrorResponse:
      $ref: '#/components/schemas/ErrorResponse'
```

# Backend / Frontend / Docs / Test Handoff

## Backend Structure Hint
- Spring Boot preferred split:
  - `global`: exception handling, `ErrorResponse`, shared infra config
  - `common`: enum such as `TaskStatus`
  - `domain/task`: controller, application service, repository, persistence
- Controller contract must stay aligned with:
  - `GET /api/v1/tasks` -> `TaskListResponse`
  - `GET|POST|PATCH` detail mutations -> `TaskResponse`
  - `DELETE` -> `ResponseEntity<Void>` with `204`

## FastAPI Structure Hint
- If reimplemented in Python:
  - `app/global`: exception handlers and app-wide middleware
  - `app/common`: enums and shared Pydantic schemas
  - `app/domain/task`: router, service, repository

## Frontend Reuse Table

| Use Case | Method/Path | Success Parsing Rule | Error Handling Rule |
|---|---|---|---|
| List screen | `GET /api/v1/tasks` | read `payload.items` | show `payload.message` when present |
| Detail screen | `GET /api/v1/tasks/{id}` | read `payload.data` | on `404`, treat as deleted/missing resource |
| Create form | `POST /api/v1/tasks` | read `payload.data` | surface validation message directly |
| Status toggle | `PATCH /api/v1/tasks/{id}/status` | read `payload.data` | keep enum options fixed to `PENDING`, `DONE` |
| Delete action | `DELETE /api/v1/tasks/{id}` | do not parse response body | treat `204` as success with empty body |

## Test Reuse Table

| Case | Expected Status | Expected Body |
|---|---|---|
| create success | `201` | `data.id`, `data.status=PENDING` |
| create missing title | `400` | `code=VALIDATION_ERROR`, `message=title is required` |
| list success | `200` | `items` array, `count` integer |
| detail invalid UUID | `400` | `code=VALIDATION_ERROR`, `message=id must be a valid UUID` |
| detail not found | `404` | `code=TASK_NOT_FOUND` |
| status update success | `200` | `data.status=DONE` |
| status invalid enum | `400` | `code=VALIDATION_ERROR`, `message=status must be one of [PENDING, DONE]` |
| status missing field | `400` | `code=VALIDATION_ERROR`, `message=status is required` |
| delete success | `204` | empty body |
| delete after re-fetch | `404` | `code=TASK_NOT_FOUND` |

## Review Drift Points
- path drift: `/api/v1/tasks` prefix must remain unchanged
- response wrapper drift: list=`{items,count}`, detail/create/update=`{data}`
- status enum drift: only `PENDING`, `DONE`
- delete drift: `204` with empty body only
- error drift: `code`, `message`, `path`, `timestamp` required on error payload
- message drift: user-readable validation text must stay stable enough for UI/tests

# Validation Results
- `api.md` required endpoint 5개 모두 정의됨.
- request/response/error payload에 placeholder, TODO, pseudocode 없음.
- `title required`, `status enum`, `404 not found`, `error payload(code/message/path/timestamp)` 제약 반영 완료.
- backend 구현 확인:
  - `TaskController` path and wrapper shape 일치
  - `GlobalExceptionHandler` error code/message/path/timestamp 일치
  - `TaskControllerTest`가 `200/201/204/400/404`와 invalid UUID/missing field/enum failure를 검증
- frontend 구현 확인:
  - `frontend/src/api.js`가 `204` empty body 처리와 `payload.message` fallback 사용

# Changed Files
- /workspace/projects/sample-service/api-handoff.md

