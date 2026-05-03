---
id: todo-service-api
type: api
version: 1.1.0
owner_agent: api
status: draft
depends_on: [product]
---

# 목적
Todo 서비스의 CRUD API와 UI/문서/테스트가 함께 참조할 구현 계약을 정의한다.

# 입력
## 도메인 모델
- Aggregate: Todo
- Entity: TodoItem
- Primary Key: Long

## 구조 규칙
### Spring Boot (`global / common / domain`)
- `com.specyn.generated.todo.global.config`
- `com.specyn.generated.todo.global.error`
- `com.specyn.generated.todo.global.response`
- `com.specyn.generated.todo.common.annotation`
- `com.specyn.generated.todo.common.util`
- `com.specyn.generated.todo.domain.todo.api`
- `com.specyn.generated.todo.domain.todo.application`
- `com.specyn.generated.todo.domain.todo.domain`
- `com.specyn.generated.todo.domain.todo.infrastructure`

### FastAPI / LangChain (필요 시)
- `app/global/config.py`
- `app/global/exception_handlers.py`
- `app/global/middleware.py`
- `app/common/schemas/`
- `app/common/utils/`
- `app/domain/todo/api.py`
- `app/domain/todo/application/`
- `app/domain/todo/domain/`
- `app/domain/todo/infrastructure/`

## 엔드포인트
| Method | Path | 설명 | 인증 | 비고 |
|---|---|---|---|---|
| GET | /api/v1/todos | 전체 목록 조회 | 없음 | 최신 생성 순 정렬 |
| GET | /api/v1/todos/{id} | 단건 조회 | 없음 | 404 처리 |
| POST | /api/v1/todos | 생성 | 없음 | title 필수 |
| PATCH | /api/v1/todos/{id}/status | 상태 변경 | 없음 | PENDING/DONE |
| DELETE | /api/v1/todos/{id} | 삭제 | 없음 | 성공 시 204 |

## 요청/응답 예시
### POST /api/v1/todos Request
```json
{
  "title": "문서 작성",
  "description": "Specyn README 업데이트"
}
```

### POST /api/v1/todos Response
```json
{
  "id": 1,
  "title": "문서 작성",
  "description": "Specyn README 업데이트",
  "status": "PENDING"
}
```

### PATCH /api/v1/todos/{id}/status Request
```json
{
  "status": "DONE"
}
```

## 오류 정책
- 400: title 누락, status 값 오류
- 404: 존재하지 않는 Todo
- 500: 내부 처리 오류

## 보안/운영 제약
- 인증은 적용하지 않는다.
- 입력 검증은 요청 DTO에서 수행한다.
- 예외 응답은 `code`, `message`, `path`, `timestamp` 필드를 가진다.
- UI는 생성/상태 변경/삭제 후 목록을 재동기화할 수 있어야 한다.

# 출력
- endpoint / schema / error contract
- Backend/Frontend/Test/Docs Agent handoff
- OpenAPI 입력 정보

# 실행 규칙
1. Spring Boot는 `global / common / domain` 구조를 우선한다.
2. `domain.todo.application`은 유스케이스와 서비스, `domain.todo.domain`은 핵심 모델/정책, `domain.todo.infrastructure`는 저장소/외부 연동을 담당한다.
3. FastAPI/LangChain이 필요하면 `app/global / app/common / app/domain` 구조를 우선한다.
4. 응답은 DTO를 사용한다.
5. unified diff가 가능하면 diff를 우선한다.

# Validation 기준
- 모든 endpoint에 request/response 예시가 있어야 한다.
- 오류 정책이 정의되어야 한다.
- 구조 규칙이 명시되어야 한다.
- 보안/운영 제약이 존재해야 한다.

# Prompt
## Role
당신은 Specyn API Agent다. Todo 서비스에 대해 Backend/Frontend/Test/Docs가 모두 재사용할 수 있는 API 계약을 정제한다.

## Instructions
1. endpoint, request/response, error model을 명확히 고정한다.
2. Spring Boot는 `global / common / domain` 구조를, FastAPI는 `app/global / app/common / app/domain` 구조를 기준으로 handoff를 정리한다.
3. validation annotation과 표준 에러 응답 기준을 반영한다.
4. TODO와 placeholder를 남기지 않는다.
5. 테스트와 문서화가 쉬운 구조를 우선한다.
6. 변경 파일과 validation 결과를 반드시 남긴다.

## Format
1. 작업 요약
2. 변경 파일 목록
3. validation 결과
4. patch 또는 전체 파일 내용
5. 다음 Agent 전달사항
