# Sample Service

이 문서는 `specyn run` 로컬 실행 결과로 생성된 sample-service CRUD 데모 요약입니다.

## 프로젝트 요약
Specyn 사용자가 `specyn.py run`까지 실행했을 때 실제로 생성 결과를 눈으로 확인할 수 있는 간단한 작업 관리 웹사이트의 요구사항을 정의한다.

## 실행된 Agent
- planner
- design
- api
- backend
- frontend
- dba
- devops
- test
- code-analysis
- security
- performance
- review
- docs
- final-review

## 생성된 확인 포인트
- Frontend: `/generated/sample-service` 라우트
- Backend summary: `/api/v1/generated/sample-service/summary`
- Backend CRUD: `/api/v1/tasks`, `/api/v1/tasks/{id}`, `/api/v1/tasks/{id}/status`
- AI Server: `/generated/sample-service/context`

## Endpoint 초안
- `GET /api/v1/tasks` · 작업 목록 조회
- `GET /api/v1/tasks/{id}` · 작업 단건 조회
- `POST /api/v1/tasks` · 작업 생성
- `PATCH /api/v1/tasks/{id}/status` · 작업 상태 변경
- `DELETE /api/v1/tasks/{id}` · 작업 삭제

## 실제 확인 순서
1. `python scripts/specyn_tasks.py dev` 로 전체 스택을 실행합니다.
2. `http://localhost:3000` 에 접속해 generated sample-service 화면을 확인합니다.
3. 새 작업을 생성하고 상세 보기를 눌러 개별 GET 응답을 확인합니다.
4. 상태 토글과 삭제를 수행해 프런트엔드와 백엔드가 함께 반응하는지 확인합니다.
