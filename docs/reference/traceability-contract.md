# Traceability Contract

Agent 출력에 가벼운 trace metadata를 남기면, 이후 dashboard / run history / reviewer audit 기능으로 확장하기 쉬워집니다.

## 권장 필드

| 필드 | 의미 |
|---|---|
| `STEP_LABEL` | 현재 실행 단계 식별자 |
| `AGENT` | agent 이름 |
| `PHASE` | base 또는 feedback |
| `FEEDBACK_ROUND` | 라운드 번호 |
| `STATUS` | done / blocked / no-material-change |
| `CHANGED_FILES` | 실제 변경 파일 |
| `RESOLVED` | 해결된 항목 |
| `UNRESOLVED` | 남은 이슈 |
| `BLOCKERS` | 즉시 중단 사유 |
| `NEXT_HANDOFF` | 다음 Agent 전달사항 |

## 예시

```text
STEP_LABEL: 05-api-api-backend-contract-sync-r1
AGENT: api
PHASE: feedback
FEEDBACK_ROUND: 1
STATUS: done
CHANGED_FILES:
- specs/projects/sample/api.md
RESOLVED:
- createUser 응답 모델 필드명을 userId로 통일
UNRESOLVED:
- 없음
BLOCKERS:
- 없음
NEXT_HANDOFF:
- Backend Agent는 응답 DTO와 OpenAPI 예시를 동일 명칭으로 맞춥니다.
```
