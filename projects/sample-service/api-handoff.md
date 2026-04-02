STEP_LABEL: api
AGENT: api
PHASE: feedback
FEEDBACK_ROUND: 2
STATUS: done
CHANGED_FILES:
- /workspace/projects/sample-service/api-handoff.md
RESOLVED:
- Trace metadata normalized to full handoff contract fields.
- API contract remains deterministic for 5 endpoints and shared error model.
UNRESOLVED:
- Runtime execution evidence is pending in test/devops phase.
BLOCKERS:
- none
NEXT_HANDOFF:
- Backend: Keep `/api/v1/tasks` paths, status codes, and error codes unchanged.
- Frontend: Treat `DELETE 204` as empty body; use `error.message` for feedback.
- Test: Validate `200/201/204/400/404`, invalid UUID, missing title, invalid status enum.
- Docs/Review: Verify wrapper shapes `{items,count}` and `{data}` plus error payload consistency.

# API Handoff: sample-service (v1)

## 1) Work Summary
- Scope: Task CRUD API contract shared across backend/frontend/test/docs.
- Base path: `/api/v1/tasks`
- Goal: deterministic endpoint, request/response schema, and error model aligned with `api.md` and backend implementation.

ASSUMPTION:
- `id` is UUID string (RFC 4122 format).
- `timestamp` is UTC ISO-8601 string (e.g. `2026-04-02T07:00:00Z`).

## 2) Endpoint Contract (Deterministic)

| Endpoint | Description | Request Body | Success | Failure |
|---|---|---|---|---|
| `GET /api/v1/tasks` | List tasks | none | `200 OK` (`TaskListResponse`) | `500 Internal Server Error` (`ErrorResponse`) |
| `GET /api/v1/tasks/{id}` | Get task detail | none | `200 OK` (`TaskResponse`) | `400 Bad Request`, `404 Not Found` |
| `POST /api/v1/tasks` | Create task | `CreateTaskRequest` | `201 Created` (`TaskResponse`) | `400 Bad Request` |
| `PATCH /api/v1/tasks/{id}/status` | Update task status | `UpdateTaskStatusRequest` | `200 OK` (`TaskResponse`) | `400 Bad Request`, `404 Not Found` |
| `DELETE /api/v1/tasks/{id}` | Delete task | none | `204 No Content` | `400 Bad Request`, `404 Not Found` |

Path parameter validation:
- `id`: required UUID format.
- invalid `id` format returns `400` with `code=VALIDATION_ERROR`.

## 3) Schemas

### 3.1 Domain Model

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
      minLength: 1
      maxLength: 200
    description:
      type: string
      maxLength: 2000
      nullable: true
    status:
      type: string
      enum: [PENDING, DONE]
    createdAt:
      type: string
      format: date-time
    updatedAt:
      type: string
      format: date-time
```

### 3.2 Request Models

```yaml
CreateTaskRequest:
  type: object
  required: [title]
  properties:
    title:
      type: string
      minLength: 1
      maxLength: 200
    description:
      type: string
      maxLength: 2000

UpdateTaskStatusRequest:
  type: object
  required: [status]
  properties:
    status:
      type: string
      enum: [PENDING, DONE]
```

### 3.3 Response Models

```yaml
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

## 4) Error Contract

```yaml
ErrorResponse:
  type: object
  required: [code, message, path, timestamp]
  properties:
    code:
      type: string
      enum:
        - VALIDATION_ERROR
        - TASK_NOT_FOUND
        - INTERNAL_ERROR
    message:
      type: string
    path:
      type: string
    timestamp:
      type: string
      format: date-time
```

Error code mapping:
- `400 Bad Request` -> `VALIDATION_ERROR`
- `404 Not Found` -> `TASK_NOT_FOUND`
- `500 Internal Server Error` -> `INTERNAL_ERROR`

Validation message rules:
- field-focused readable message.
- canonical examples:
  - `title is required`
  - `status must be one of [PENDING, DONE]`
  - `id must be a valid UUID`

## 5) Request/Response Examples

### GET /api/v1/tasks

`200 OK`

```json
{
  "items": [
    {
      "id": "6d3237ae-570f-4c8c-b3aa-b6d56c87f5c5",
      "title": "Write API contract",
      "description": "Prepare deterministic spec",
      "status": "PENDING",
      "createdAt": "2026-04-02T07:00:00Z",
      "updatedAt": "2026-04-02T07:00:00Z"
    }
  ],
  "count": 1
}
```

### GET /api/v1/tasks/{id}

`404 Not Found`

```json
{
  "code": "TASK_NOT_FOUND",
  "message": "Task not found: 6d3237ae-570f-4c8c-b3aa-b6d56c87f5c5",
  "path": "/api/v1/tasks/6d3237ae-570f-4c8c-b3aa-b6d56c87f5c5",
  "timestamp": "2026-04-02T07:10:00Z"
}
```

### POST /api/v1/tasks

Request

```json
{
  "title": "Implement backend",
  "description": "Create REST endpoints"
}
```

`201 Created`

```json
{
  "data": {
    "id": "f6dbb4e1-48ac-4d11-88f8-1313f955a9ff",
    "title": "Implement backend",
    "description": "Create REST endpoints",
    "status": "PENDING",
    "createdAt": "2026-04-02T07:20:00Z",
    "updatedAt": "2026-04-02T07:20:00Z"
  }
}
```

### PATCH /api/v1/tasks/{id}/status

Request

```json
{
  "status": "DONE"
}
```

`400 Bad Request` (invalid enum)

```json
{
  "code": "VALIDATION_ERROR",
  "message": "status must be one of [PENDING, DONE]",
  "path": "/api/v1/tasks/f6dbb4e1-48ac-4d11-88f8-1313f955a9ff/status",
  "timestamp": "2026-04-02T07:31:00Z"
}
```

### DELETE /api/v1/tasks/{id}

`204 No Content` (empty body)

## 6) OpenAPI-Friendly Summary

```yaml
openapi: 3.0.3
info:
  title: sample-service API
  version: 1.0.0
paths:
  /api/v1/tasks:
    get:
      operationId: listTasks
      responses:
        '200':
          description: OK
    post:
      operationId: createTask
      responses:
        '201':
          description: Created
        '400':
          description: Bad Request
  /api/v1/tasks/{id}:
    get:
      operationId: getTask
      parameters:
        - in: path
          name: id
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: OK
        '400':
          description: Bad Request
        '404':
          description: Not Found
    delete:
      operationId: deleteTask
      responses:
        '204':
          description: No Content
        '400':
          description: Bad Request
        '404':
          description: Not Found
  /api/v1/tasks/{id}/status:
    patch:
      operationId: updateTaskStatus
      responses:
        '200':
          description: OK
        '400':
          description: Bad Request
        '404':
          description: Not Found
```

## 7) Reusable Handoff

Backend (Spring Boot):
- `global`: `GlobalExceptionHandler`, `ErrorResponse`, exception mapping.
- `common`: `TaskStatus` enum and reusable validators.
- `domain/task`: controller/service/repository split.
- keep `DELETE` as `204` with empty body.

Backend (FastAPI reference if re-implemented):
- `app/global`: exception handlers/middleware.
- `app/common`: pydantic enums/models.
- `app/domain/task`: router/service/repository.

Frontend:
- status domain fixed to `PENDING | DONE`.
- on delete success, do not parse JSON body (`204`).
- show `error.message` directly in user feedback.

Test:
- cover `200`, `201`, `204`, `400`, `404`.
- include invalid UUID, missing title, invalid status enum.
- verify delete then detail returns `404 TASK_NOT_FOUND`.

Docs:
- keep response wrapper shape exactly: list=`{items,count}`, detail/create/update=`{data}`.
- keep error payload shape exactly: `code,message,path,timestamp`.

Review drift points:
- path/version drift (`/api/v1/tasks`).
- status enum drift (`PENDING`,`DONE`).
- delete response drift (`204` + empty body).
- error code drift (`VALIDATION_ERROR`,`TASK_NOT_FOUND`,`INTERNAL_ERROR`).

## 8) Feedback Round Delta
- Resolved: API handoff format normalized for trace metadata and backend contract reuse.
- Resolved: backend-implemented validation/error messages reflected in examples.
- Unresolved: runtime execution proof is owned by test/devops steps (API contract side completed).
