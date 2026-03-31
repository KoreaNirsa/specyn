# Sample Service Generated Test Plan

## 목적
Specyn 사용자가 `specyn.py run`까지 실행했을 때 실제로 생성 결과를 눈으로 확인할 수 있는 간단한 작업 관리 웹사이트의 요구사항을 정의한다.

## 우선 검증 시나리오
- POST /api/v1/tasks 요청 시 201과 생성된 Task payload를 반환한다.
- GET /api/v1/tasks 요청 시 seeded task와 신규 task를 포함한 목록을 반환한다.
- GET /api/v1/tasks/{id} 에서 존재하지 않는 ID 조회 시 404를 반환한다.
- PATCH /api/v1/tasks/{id}/status 에서 잘못된 status 값 입력 시 400을 반환한다.
- PATCH /api/v1/tasks/{id}/status 성공 시 상태가 `DONE` 또는 `PENDING` 으로 갱신된다.
- DELETE /api/v1/tasks/{id} 성공 후 재조회 시 404를 확인한다.
- generated frontend page는 생성/상세 조회/상태 변경/삭제를 모두 재현할 수 있어야 한다.

## 자동화 확인 포인트
- generated backend summary endpoint가 응답한다.
- GET /api/v1/tasks 로 seeded task와 새로 생성한 task를 모두 확인할 수 있다.
- POST /api/v1/tasks 로 title/description을 가진 task를 생성할 수 있다.
- PATCH /api/v1/tasks/{id}/status 로 DONE/PENDING 전환을 검증한다.
- DELETE /api/v1/tasks/{id} 이후 재조회 시 404를 확인한다.
- generated frontend page에서 생성/상태 변경/삭제를 수동 QA로 재현한다.
