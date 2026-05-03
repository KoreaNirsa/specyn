---
id: tdd-workflow-api
type: api
version: 1.0.0
owner_agent: api
status: draft
depends_on: [product]
---

# 목적
TDD 결과를 handoff와 PR 설명에 남길 때 사용할 구조적 계약을 정의한다.

# 입력
## 엔드포인트
| Method | Path | Request | Response | Owner |
|---|---|---|---|---|
| N/A | test-handoff | TddEvidence | TddResult | test |

## 요청/응답 예시
### Request
```json
{
  "red": "test failed before implementation",
  "green": "test passed after minimal implementation",
  "refactor": "no refactor needed",
  "command": "python -m pytest tools/tests/test_spec_loader.py"
}
```

### Response
```json
{
  "status": "verified",
  "evidence": ["red", "green"],
  "gaps": []
}
```

## 오류 정책
- Red 단계 증거가 없으면 구현 변경을 승인하지 않는다.
- Green 단계 명령이 실패하면 작업을 완료로 보지 않는다.
- 테스트 불가능 항목은 gaps에 남기고 수동 검증 기준을 요구한다.

# 출력
- TDD evidence 구조
- 검증 명령 기록 기준
- 테스트 gap 처리 기준

# 실행 규칙
1. 새 HTTP API를 추가하지 않는다.
2. 이 문서는 handoff와 PR 설명에 들어갈 evidence 구조로 사용한다.
3. command는 실제 실행한 명령만 기록한다.
4. gaps는 구현 완료와 분리해서 남긴다.

# Validation 기준
- 엔드포인트 표에는 최소 1개 이상의 계약 row가 있어야 한다.
- 요청/응답 예시는 Request와 Response를 모두 포함해야 한다.
- 오류 정책은 비어 있으면 안 된다.

# Prompt
## Role
당신은 API Agent로서 TDD evidence 구조를 계약화한다.

## Instructions
1. 실행하지 않은 검증 명령을 기록하지 않는다.
2. red/green/refactor evidence를 분리한다.
3. gaps는 남은 위험으로 표시한다.

## Format
1. evidence schema
2. request example
3. response example
4. error policy
