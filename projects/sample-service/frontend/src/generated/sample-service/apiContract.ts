export const generatedApiContract = {
  "projectId": "sample-service",
  "title": "Sample Service",
  "summary": "Specyn 사용자가 `specyn.py run`까지 실행했을 때 실제로 생성 결과를 눈으로 확인할 수 있는 간단한 작업 관리 웹사이트의 요구사항을 정의한다.",
  "scenarios": [
    "사용자가 generated 페이지에서 제목과 설명을 입력해 새 작업을 생성한다.",
    "사용자가 작업 목록을 확인하고 특정 작업의 상세 JSON 응답을 본다.",
    "사용자가 작업 상태를 `PENDING` ↔ `DONE` 으로 전환한다.",
    "사용자가 잘못 만든 작업을 삭제하고 목록이 즉시 갱신되는 것을 확인한다.",
    "개발자는 동일한 spec bundle로 API 계약, generated frontend, generated backend, generated docs가 함께 갱신되는지 확인한다."
  ],
  "nonFunctionalRequirements": [
    "UX: generated 페이지는 로딩/빈 상태/오류 상태를 구분해서 보여주고, 버튼만으로 CRUD 흐름을 재현할 수 있어야 한다.",
    "성능: 단건/목록 요청은 로컬 개발 환경 기준 즉시 반응하며 p95 500ms 이내를 목표로 한다.",
    "보안: 인증은 적용하지 않지만 입력 검증, 표준 오류 응답, 민감 정보 로그 금지 원칙을 따른다.",
    "운영: 별도 DB 없이도 dev 환경에서 동작해야 하며 재실행 시 초기 seeded task가 준비되어야 한다.",
    "문서: 사용자 문서가 `run` 명령, 옵션, 확인 URL, expected result를 모두 포함해야 한다."
  ],
  "reviewRules": [
    "Spring Boot generated controller는 endpoint 동작이 실제로 재현되어야 하며 placeholder 응답이면 안 된다.",
    "generated frontend page는 API 계약을 숨기지 말고 summary/contract/result를 함께 보여줘야 한다.",
    "DTO/응답 구조는 상태코드와 함께 일관되게 유지한다.",
    "generated docs는 사용자가 그대로 따라 할 수 있는 실행 절차를 포함해야 한다.",
    "title 입력 검증 누락은 blocker로 본다.",
    "내부 예외/스택트레이스를 사용자 응답에 노출하면 major 이상으로 본다.",
    "민감 정보 로그 출력은 blocker로 본다."
  ],
  "testScenarios": [
    "POST /api/v1/tasks 요청 시 201과 생성된 Task payload를 반환한다.",
    "GET /api/v1/tasks 요청 시 seeded task와 신규 task를 포함한 목록을 반환한다.",
    "GET /api/v1/tasks/{id} 에서 존재하지 않는 ID 조회 시 404를 반환한다.",
    "PATCH /api/v1/tasks/{id}/status 에서 잘못된 status 값 입력 시 400을 반환한다.",
    "PATCH /api/v1/tasks/{id}/status 성공 시 상태가 `DONE` 또는 `PENDING` 으로 갱신된다.",
    "DELETE /api/v1/tasks/{id} 성공 후 재조회 시 404를 확인한다.",
    "generated frontend page는 생성/상세 조회/상태 변경/삭제를 모두 재현할 수 있어야 한다."
  ],
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/v1/tasks",
      "description": "작업 목록 조회",
      "auth": "없음",
      "note": "seeded task + 생성된 task를 함께 반환",
      "operationId": "get_api_v1_tasks"
    },
    {
      "method": "GET",
      "path": "/api/v1/tasks/{id}",
      "description": "작업 단건 조회",
      "auth": "없음",
      "note": "존재하지 않으면 404",
      "operationId": "get_api_v1_tasks_by_id"
    },
    {
      "method": "POST",
      "path": "/api/v1/tasks",
      "description": "작업 생성",
      "auth": "없음",
      "note": "`title` 필수",
      "operationId": "post_api_v1_tasks"
    },
    {
      "method": "PATCH",
      "path": "/api/v1/tasks/{id}/status",
      "description": "작업 상태 변경",
      "auth": "없음",
      "note": "`PENDING`, `DONE` 만 허용",
      "operationId": "patch_api_v1_tasks_by_id_status"
    },
    {
      "method": "DELETE",
      "path": "/api/v1/tasks/{id}",
      "description": "작업 삭제",
      "auth": "없음",
      "note": "성공 시 204",
      "operationId": "delete_api_v1_tasks_by_id"
    }
  ],
  "errorPolicies": [
    "400: `title` 누락, `status` 값 오류",
    "404: 존재하지 않는 Task 조회/삭제/상태 변경",
    "500: 내부 처리 오류"
  ],
  "requestExample": {
    "title": "README 업데이트",
    "description": "sample-service generated 페이지 확인"
  },
  "responseExample": {
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
  },
  "executionFlow": [
    "planner",
    "design",
    "api",
    "backend",
    "frontend",
    "dba",
    "devops",
    "test",
    "code-analysis",
    "security",
    "performance",
    "review",
    "docs",
    "final-review"
  ],
  "supportedAgents": [
    "planner",
    "design",
    "api",
    "backend",
    "frontend",
    "dba",
    "devops",
    "test",
    "code-analysis",
    "security",
    "performance",
    "review",
    "docs",
    "final-review",
    "rag",
    "orchestrator"
  ],
  "optionalAgents": [
    "rag"
  ],
  "ragEnabled": false
} as const;
            export type GeneratedApiEndpoint = typeof generatedApiContract.endpoints[number];
            export type GeneratedApiManifest = typeof generatedApiContract;
