---
id: sample-service-api
type: api
version: 1.2.0
owner_agent: api
status: draft
depends_on: [product]
---

# 목적
sample-service generated CRUD 웹사이트와 backend가 함께 사용할 작업(Task) 관리 API 계약을 정의한다.

# 입력
## 도메인 모델
- Aggregate: TaskBoard
- Entity: TaskItem
- Primary Key: Long

## 구조 규칙
### Spring Boot (`global / common / domain`)
- `com.specyn.generated.sample.global.config`
- `com.specyn.generated.sample.global.error`
- `com.specyn.generated.sample.global.response`
- `com.specyn.generated.sample.common.annotation`
- `com.specyn.generated.sample.common.util`
- `com.specyn.generated.sample.domain.task.api`
- `com.specyn.generated.sample.domain.task.application`
- `com.specyn.generated.sample.domain.task.domain`
- `com.specyn.generated.sample.domain.task.infrastructure`

### FastAPI / LangChain (필요 시)
- `app/global/config.py`
- `app/global/exception_handlers.py`
- `app/global/middleware.py`
- `app/common/schemas/`
- `app/common/utils/`
- `app/domain/task/api.py`
- `app/domain/task/application/`
- `app/domain/task/domain/`
- `app/domain/task/infrastructure/`

## 엔드포인트
| Method | Path | 설명 | 인증 | 비고 |
|---|---|---|---|---|
| GET | /api/v1/tasks | 작업 목록 조회 | 없음 | seeded task + 생성된 task를 함께 반환 |
| GET | /api/v1/tasks/{id} | 작업 단건 조회 | 없음 | 존재하지 않으면 404 |
| POST | /api/v1/tasks | 작업 생성 | 없음 | `title` 필수 |
| PATCH | /api/v1/tasks/{id}/status | 작업 상태 변경 | 없음 | `PENDING`, `DONE` 만 허용 |
| DELETE | /api/v1/tasks/{id} | 작업 삭제 | 없음 | 성공 시 204 |

## 요청/응답 예시
### GET /api/v1/tasks Response
```json
{
  "items": [
    {
      "id": 2,
      "title": "런타임 확인",
      "description": "새 항목을 추가하고 상태를 변경한 뒤 삭제까지 확인합니다.",
      "status": "PENDING",
      "createdAt": "2026-03-30T04:00:00Z",
      "updatedAt": "2026-03-30T04:00:00Z"
    }
  ],
  "count": 1
}
```

### GET /api/v1/tasks/{id} Response
```json
{
  "item": {
    "id": 2,
    "title": "런타임 확인",
    "description": "새 항목을 추가하고 상태를 변경한 뒤 삭제까지 확인합니다.",
    "status": "PENDING",
    "createdAt": "2026-03-30T04:00:00Z",
    "updatedAt": "2026-03-30T04:00:00Z"
  }
}
```

### POST /api/v1/tasks Request
```json
{
  "title": "README 업데이트",
  "description": "sample-service generated 페이지 확인"
}
```

### POST /api/v1/tasks Response
```json
{
  "item": {
    "id": 3,
    "title": "README 업데이트",
    "description": "sample-service generated 페이지 확인",
    "status": "PENDING",
    "createdAt": "2026-03-30T04:00:00Z",
    "updatedAt": "2026-03-30T04:00:00Z"
  },
  "count": 3
}
```

### PATCH /api/v1/tasks/{id}/status Request
```json
{
  "status": "DONE"
}
```

### PATCH /api/v1/tasks/{id}/status Response
```json
{
  "item": {
    "id": 3,
    "title": "README 업데이트",
    "description": "sample-service generated 페이지 확인",
    "status": "DONE",
    "createdAt": "2026-03-30T04:00:00Z",
    "updatedAt": "2026-03-30T04:05:00Z"
  }
}
```

### DELETE /api/v1/tasks/{id} Response
```json
{
  "status": 204,
  "body": null
}
```

## 오류 정책
- 400: `title` 누락, `status` 값 오류
- 404: 존재하지 않는 Task 조회/삭제/상태 변경
- 500: 내부 처리 오류

## 보안/운영 제약
- 인증은 사용하지 않는다.
- 오류 응답은 `code`, `message`, `path`, `timestamp` 필드를 포함해야 한다.
- generated frontend는 성공 후 목록과 summary를 다시 조회해 상태를 동기화해야 한다.
- 민감 정보 로그 출력은 금지한다.
- dev 재실행 시 샘플 데이터가 다시 준비되어도 무방하다.

# 출력
- frontend/backend/test/docs가 함께 참조할 Task CRUD 계약
- generated project page가 사용할 request/response 규약
- OpenAPI와 테스트 시나리오에 그대로 반영할 예시 데이터
- 운영/리뷰 단계에서 확인할 오류 응답 기준

# 실행 규칙
1. endpoint 경로와 상태코드는 deterministic 해야 한다.
2. `GET /api/v1/tasks` 는 목록과 count를 함께 반환한다.
3. `GET /api/v1/tasks/{id}` 와 `POST/PATCH` 는 `item` wrapper를 사용한다.
4. `POST /api/v1/tasks` 는 title 검증 실패 시 400을 반환해야 한다.
5. `PATCH /api/v1/tasks/{id}/status` 는 상태 전환 전용 API로 유지한다.
6. `DELETE /api/v1/tasks/{id}` 는 성공 시 204를 반환한다.
7. placeholder endpoint나 TODO 응답을 남기지 않는다.

# Validation 기준
- 모든 endpoint에 request/response 예시가 있어야 한다.
- 오류 정책이 정의되어야 한다.
- Spring Boot와 필요 시 FastAPI 구조 규칙이 명시되어야 한다.
- 보안/운영 제약이 존재해야 한다.

# Prompt
## Role
당신은 Specyn API Agent다. sample-service generated CRUD 데모에 바로 적용할 수 있는 Task API 계약을 정제한다.

## Instructions
1. generated frontend가 그대로 호출할 수 있도록 endpoint와 상태코드를 고정한다.
2. request/response/error model을 테스트 친화적으로 정리한다.
3. Spring Boot는 `global / common / domain`, FastAPI는 `app/global / app/common / app/domain` 구조를 기본으로 설계한다.
4. 삭제 성공 204, validation 400, not-found 404 규칙을 분명히 남긴다.
5. Docs/Test/Review Agent가 재사용할 handoff를 포함한다.

## Format
1. 작업 요약
2. 변경 파일 목록
3. validation 결과
4. patch 또는 전체 파일 내용
5. 다음 Agent(Backend/Frontend/Test/Docs)에 전달할 체크포인트
