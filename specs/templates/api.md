---
id: {{project_id}}-api
type: api
version: 1.1.0
owner_agent: api
status: draft
depends_on: [product]
---

# 목적
이 문서는 Spring Boot API 구현과 프론트엔드/문서/테스트가 함께 참조할 수 있는 계약을 정의한다.

# 입력
## 도메인 모델
- Aggregate:
- Entity:
- Primary Key:

## 구조 규칙
### Spring Boot (`global / common / domain`)
- `com.specyn.generated.<service>.global.config`
- `com.specyn.generated.<service>.global.error`
- `com.specyn.generated.<service>.global.response`
- `com.specyn.generated.<service>.common.annotation`
- `com.specyn.generated.<service>.common.util`
- `com.specyn.generated.<service>.domain.<bounded_context>.api`
- `com.specyn.generated.<service>.domain.<bounded_context>.application`
- `com.specyn.generated.<service>.domain.<bounded_context>.domain`
- `com.specyn.generated.<service>.domain.<bounded_context>.infrastructure`

### FastAPI / LangChain (필요 시)
- `app/global/config.py`
- `app/global/exception_handlers.py`
- `app/global/middleware.py`
- `app/common/schemas/`
- `app/common/utils/`
- `app/domain/<bounded_context>/api.py`
- `app/domain/<bounded_context>/application/`
- `app/domain/<bounded_context>/domain/`
- `app/domain/<bounded_context>/infrastructure/`

## 엔드포인트
| Method | Path | 설명 | 인증 | 비고 |
|---|---|---|---|---|
| GET | /api/v1/example | 목록 조회 | 없음 | |
| POST | /api/v1/example | 생성 | 없음 | |

## 요청/응답 예시
### Request
```json
{
  "field": "value"
}
```

### Response
```json
{
  "id": 1,
  "field": "value"
}
```

## 오류 정책
- 400: 잘못된 입력
- 404: 리소스 없음
- 409: 충돌
- 500: 내부 오류

## 보안/운영 제약
- 인증 필요 여부
- 민감 정보 로그 금지 여부
- idempotency / transaction 제약
- 프론트엔드 소비 시 필요한 오류/상태 처리 규칙

# 출력
- endpoint / schema / error contract
- Backend 구현과 문서화에 필요한 OpenAPI 입력 정보
- Frontend/Test Agent가 재사용할 request/response 예시

# 실행 규칙
1. 상태코드, 필드명, 에러코드는 deterministic 해야 한다.
2. Spring Boot는 `global / common / domain` 구조를 우선한다.
3. 도메인 로직은 `domain.<bounded_context>.application / domain / infrastructure` 경계로 분리한다.
4. FastAPI/LangChain이 필요하면 `app/global / app/common / app/domain` 구조를 우선한다.
5. placeholder 코드와 TODO를 남기지 않는다.
6. 기존 파일이 있으면 unified diff patch를 우선한다.

# Validation 기준
- 모든 endpoint에 요청/응답 예시가 있어야 한다.
- 오류 정책이 정의되어야 한다.
- Spring Boot와 필요 시 FastAPI 구조 규칙이 명시되어야 한다.
- 보안/운영 제약이 존재해야 한다.

# Prompt
## Role
당신은 Specyn API Agent다. 실제 구현과 문서화에 바로 사용할 수 있는 API 계약을 정제한다.

## Instructions
1. `spec.md`와 본 문서를 source of truth로 사용한다.
2. endpoint, request/response, error model을 명확히 고정한다.
3. Spring Boot는 `global / common / domain` 구조를, FastAPI는 `app/global / app/common / app/domain` 구조를 기본으로 설계한다.
4. 입력 검증, 표준 에러 응답, 테스트 친화적인 경계를 만든다.
5. 보안/운영 제약을 무시하지 않는다.
6. 다음 Agent가 바로 사용할 수 있는 handoff를 남긴다.

## Format
다음 순서로 출력한다.
1. 작업 요약
2. 변경 파일 목록
3. validation 결과
4. patch 또는 전체 파일 내용
5. 다음 Agent(Backend/Frontend/Test/Docs)에 전달할 체크포인트
