---
id: dashboard-design-api
type: api
version: 1.0.0
owner_agent: api
status: draft
depends_on: [product]
---

# 목적
Design.md가 참조하는 dashboard API와 runtime endpoint 계약을 정리한다.

# 입력
## 엔드포인트
| Method | Path | Request | Response | Owner |
|---|---|---|---|---|
| GET | /api/v1/spec-runs/health | none | HealthResponse | dashboard-backend |
| POST | /api/v1/spec-runs | SpecRunRequest | SpecRunResponse | dashboard-backend |
| POST | /api/v1/spec-runs/stream | SpecRunRequest | NDJSON SpecRunStreamEvent | dashboard-backend |
| GET | /health | none | HealthResponse | dashboard-ai-server |

## 요청/응답 예시
### Request
```json
{
  "projectId": "sample-service",
  "workspacePath": "projects/sample-service",
  "ragEnabled": false,
  "dryRun": false,
  "documents": []
}
```

### Response
```json
{
  "status": "UP"
}
```

## 오류 정책
- backend 또는 AI server health 확인 실패는 화면에서 down 상태로 표시한다.
- stream request 실패는 사용자에게 원인 메시지를 노출한다.
- invalid spec bundle은 backend validator 오류로 처리한다.

# 출력
- Design.md에서 참조할 API endpoint 목록
- health, run, stream의 요청/응답 기준
- 오류 표시 기준

# 실행 규칙
1. 신규 API를 정의하지 않는다.
2. 현재 구현된 client.ts와 SpecRunController 기준만 사용한다.
3. streaming 응답은 application/x-ndjson 계약으로 설명한다.
4. sample-service runtime endpoint는 dashboard 디자인 보조 정보로만 둔다.

# Validation 기준
- 엔드포인트 표에는 최소 1개 이상의 endpoint가 있어야 한다.
- 요청/응답 예시는 Request와 Response를 모두 포함해야 한다.
- 오류 정책은 비어 있으면 안 된다.

# Prompt
## Role
당신은 API Agent로서 dashboard design 스펙이 의존하는 API 계약을 정리한다.

## Instructions
1. client.ts와 controller에 존재하는 endpoint만 작성한다.
2. 디자인 스펙이 상태를 판단할 수 있는 응답 필드를 명시한다.
3. 신규 API 요구사항은 TODO로 남긴다.

## Format
1. endpoint table
2. request examples
3. response examples
4. error policy
