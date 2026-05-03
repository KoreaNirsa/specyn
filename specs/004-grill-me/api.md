---
id: grill-me-api
type: api
version: 1.0.0
owner_agent: api
status: draft
depends_on: [product]
---

# 목적
Grill Me 결과를 handoff에 남길 때 사용할 구조적 계약을 정의한다.

# 입력
## 엔드포인트
| Method | Path | Request | Response | Owner |
|---|---|---|---|---|
| N/A | spec-handoff | GrillMeQuestionSet | GrillMeResult | review |

## 요청/응답 예시
### Request
```json
{
  "section": "Validation 기준",
  "question": "어떤 테스트가 실패하면 구현을 중단하는가?",
  "severity": "blocker"
}
```

### Response
```json
{
  "resolved": ["TDD 실패 시 구현 중단"],
  "unresolved": ["성능 기준 수치 미정"]
}
```

## 오류 정책
- 스펙 섹션과 연결되지 않은 질문은 review 입력으로 인정하지 않는다.
- 답변 없는 blocker는 final-review 통과 조건에서 제외하지 않는다.
- 질문 결과가 handoff에 없으면 Grill Me 미수행으로 본다.

# 출력
- Grill Me 질문/답변 데이터 구조
- resolved/unresolved 분리 기준
- handoff 포함 규칙

# 실행 규칙
1. HTTP API를 새로 추가하지 않는다.
2. 이 문서는 agent handoff 구조 계약으로만 사용한다.
3. 질문 severity는 blocker, major, minor 중 하나로 제한한다.
4. unresolved blocker는 구현 금지 범위로 유지한다.

# Validation 기준
- 엔드포인트 표에는 최소 1개 이상의 계약 row가 있어야 한다.
- 요청/응답 예시는 Request와 Response를 모두 포함해야 한다.
- 오류 정책은 비어 있으면 안 된다.

# Prompt
## Role
당신은 API Agent로서 Grill Me 결과 구조를 계약화한다.

## Instructions
1. 새 런타임 API를 만들지 않는다.
2. agent handoff에서 재사용 가능한 필드만 정의한다.
3. unresolved 항목은 구현 가능 범위와 분리한다.

## Format
1. contract shape
2. request example
3. response example
4. error policy
