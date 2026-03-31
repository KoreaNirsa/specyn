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
- Frontend: `http://localhost:5173`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- Backend CRUD: `http://localhost:8080/api/v1/tasks`, `http://localhost:8080/api/v1/tasks/{id}`, `http://localhost:8080/api/v1/tasks/{id}/status`
- AI Server: `http://localhost:8000/generated/sample-service/context`

## Endpoint 초안
- `GET /api/v1/tasks` · 작업 목록 조회
- `GET /api/v1/tasks/{id}` · 작업 단건 조회
- `POST /api/v1/tasks` · 작업 생성
- `PATCH /api/v1/tasks/{id}/status` · 작업 상태 변경
- `DELETE /api/v1/tasks/{id}` · 작업 삭제

## 실제 확인 순서
1. `python scripts/specyn_tasks.py sample-dev` 로 실제 프로젝트 런타임을 실행합니다.
2. Frontend는 `http://localhost:5173` 에서 확인합니다.
3. Backend summary는 `http://localhost:8080/api/v1/generated/sample-service/summary` 에서 확인합니다.
4. AI Server context는 `http://localhost:8000/generated/sample-service/context` 에서 확인합니다.
5. 새 작업을 생성하고 상세 보기를 눌러 개별 GET 응답을 확인합니다.
6. 상태 토글과 삭제를 수행해 프런트엔드와 백엔드가 함께 반응하는지 확인합니다.
