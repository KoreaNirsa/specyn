---
id: sample-service-api
type: api
version: 1.3.1
owner_agent: api
status: draft
depends_on: [product]
---

# 목적
sample-service CRUD 기능에 필요한 API contract를 정의한다.

# 입력
## 도메인 모델
- Aggregate: Task
- Entity: Task
- Primary Key: id (Long)

## 구조 규칙
### Spring Boot (`global / common / domain`)
- `com.sample.service.global.config`
- `com.sample.service.global.error`
- `com.sample.service.global.exception`
- `com.sample.service.domain.task.api`
- `com.sample.service.domain.task.application`
- `com.sample.service.domain.task.domain`
- `com.sample.service.domain.task.infrastructure`

## 엔드포인트

| Method | Path | 설명 | 인증 | 비고 |
|---|---|---|---|---|
| GET | /api/v1/tasks | Task 목록 조회 | 없음 | 최신 생성 순 정렬 |
| GET | /api/v1/tasks/{id} | Task 상세 조회 | 없음 | 존재하지 않으면 404 |
| POST | /api/v1/tasks | Task 생성 | 없음 | 제목은 필수 |
| PATCH | /api/v1/tasks/{id}/status | Task 상태 변경 | 없음 | `PENDING`, `DONE`만 허용 |
| DELETE | /api/v1/tasks/{id} | Task 삭제 | 없음 | 성공 시 204 |

## 요청/응답 예시
### Request
```json
{
  "title": "Write CI workflow"
}
```

### Response
```json
{
  "id": 1,
  "title": "Write CI workflow",
  "status": "PENDING",
  "createdAt": "2026-04-02T10:00:00Z"
}
```

## 오류 정책
- 400: 제목이 비어 있거나 상태 값이 허용 목록에 없으면 반환한다.
- 404: 존재하지 않는 Task id를 조회, 수정, 삭제하면 반환한다.
- 500: 서버 내부 오류가 발생하면 공통 에러 응답 형식으로 반환한다.

## 보안/운영 제약
- 인증 없이 로컬 샘플 서비스를 실행할 수 있어야 한다.
- 오류 응답은 `code`, `message`, `path`, `timestamp` 필드를 포함해야 한다.
- API contract는 frontend, test, docs spec이 그대로 참조할 수 있을 정도로 안정적이어야 한다.

# 출력
- endpoint / schema / error contract
- Backend 구현과 문서화에 필요한 OpenAPI 수준의 입력 정보
- Frontend/Test Agent가 사용할 request/response 예시

# 실행 규칙
1. 상태코드, 필드명, 에러 코드는 deterministic 해야 한다.
2. placeholder endpoint나 TODO 설명을 남기지 않는다.
3. 성공/실패 케이스를 모두 다룰 수 있도록 contract를 정의한다.

# Validation 기준
- 모든 endpoint가 엔드포인트 표에 정의되어 있어야 한다.
- 요청/응답 예시에 Request/Response 하위 섹션이 모두 있어야 한다.
- 오류 정책이 비어 있지 않아야 한다.

# Prompt
## Role
당신은 API Agent로서 sample-service CRUD API contract를 정리한다.

## Instructions
1. endpoint와 status code를 고정한다.
2. request/response 예시를 downstream spec이 그대로 재사용할 수 있게 작성한다.
3. 에러 응답 규칙을 명확히 적는다.

## Format
1. 작업 요약
2. 엔드포인트 목록
3. 요청/응답 예시
4. validation 체크사항
