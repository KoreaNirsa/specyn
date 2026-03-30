export const generatedApiContract = {
  "projectId": "sample-service",
  "title": "Sample Service",
  "summary": "이 문서는 서비스의 제품 목표, 사용자 가치, 성공 기준을 정의하고 downstream spec의 기준점을 제공한다.",
  "scenarios": [
    "시나리오 1",
    "시나리오 2",
    "시나리오 3"
  ],
  "nonFunctionalRequirements": [
    "보안: 예) 인증/인가, 민감정보 처리, 감사로그",
    "성능: 예) p95 응답시간, 처리량, 동시성",
    "운영: 예) 장애 탐지, 로깅, 추적성, 롤백 가능성",
    "UX: 예) 로딩/오류/접근성/반응형 기준"
  ],
  "reviewRules": [
    "Spring Boot는 `global / common / domain` 구조를 우선한다.",
    "Controller/Route는 비즈니스 로직을 직접 포함하지 않는다.",
    "DTO와 Domain 모델을 분리한다.",
    "예외 응답 구조를 통일한다.",
    "프론트엔드 상태/에러 처리와 API 계약이 정합해야 한다.",
    "입력 검증 누락은 blocker로 분류한다.",
    "민감 정보 로그 출력은 blocker로 분류한다.",
    "내부 구현 상세 예외 메시지 노출은 major 이상으로 분류한다."
  ],
  "testScenarios": [
    "성공 시나리오 1",
    "성공 시나리오 2",
    "실패 시나리오 1",
    "실패 시나리오 2"
  ],
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/v1/example",
      "description": "목록 조회",
      "auth": "없음",
      "note": "",
      "operationId": "get_api_v1_example"
    },
    {
      "method": "POST",
      "path": "/api/v1/example",
      "description": "생성",
      "auth": "없음",
      "note": "",
      "operationId": "post_api_v1_example"
    }
  ],
  "errorPolicies": [
    "400: 잘못된 입력",
    "404: 리소스 없음",
    "409: 충돌",
    "500: 내부 오류"
  ],
  "requestExample": {
    "field": "value"
  },
  "responseExample": {
    "id": 1,
    "field": "value"
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
