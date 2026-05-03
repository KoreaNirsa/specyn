---
id: todo-service-test
type: test
version: 1.1.0
owner_agent: test
status: draft
depends_on: [api]
---

# 목적
Todo 서비스 구현이 제품/계약 요구사항을 만족하는지 검증할 테스트 시나리오를 정의한다.

# 입력
## 테스트 범위
- Controller 단위 테스트
- Service 단위 테스트
- MockMvc 기반 API 테스트
- 필요 시 React 주요 사용자 흐름 smoke test

## 시나리오
1. POST /api/v1/todos 요청 시 201과 생성된 Todo를 반환한다.
2. GET /api/v1/todos 요청 시 목록을 반환한다.
3. GET /api/v1/todos/{id}에서 없는 ID 조회 시 404를 반환한다.
4. PATCH /api/v1/todos/{id}/status에서 잘못된 상태 값 입력 시 400을 반환한다.
5. DELETE /api/v1/todos/{id} 성공 시 204를 반환한다.
6. UI가 빈 목록 / 로딩 / 오류 상태를 사용자에게 구분해서 보여준다.

## 테스트 대상
- Controller
- Service
- Exception Handler
- Todo 관리 UI의 핵심 상태 전환

# 출력
- JUnit 5 테스트 코드
- MockMvc 테스트 코드
- endpoint coverage 체크리스트
- 수동 QA가 필요한 사용자 흐름 메모

# 실행 규칙
1. 모든 endpoint를 최소 1회 이상 호출한다.
2. 성공/실패 시나리오를 모두 포함한다.
3. 응답 코드와 body를 함께 검증한다.
4. 테스트 이름만 보아도 의도를 파악할 수 있어야 한다.

# Validation 기준
- endpoint coverage 100%
- 400/404 예외 케이스 포함
- 상태 변경 API의 성공/실패 케이스 포함
- 상태코드와 응답 본문 assertion 포함

# Prompt
## Role
당신은 Specyn Test Agent다. Todo 서비스 구현이 계약과 사용자 흐름을 만족하는지 검증하는 테스트를 생성한다.

## Instructions
1. 성공/실패/validation/not-found 시나리오를 모두 다룬다.
2. Controller와 Service 테스트를 역할에 맞게 분리한다.
3. 필요하면 프론트엔드 핵심 사용자 흐름 smoke test도 제안한다.
4. Review Agent가 참고할 coverage 정보를 함께 남긴다.
5. flaky test를 만들지 않는다.

## Format
1. 작업 요약
2. 생성/수정된 테스트 파일 목록
3. endpoint coverage 체크리스트
4. validation 결과
5. Review Agent 전달사항
