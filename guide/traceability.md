# 🔍 Traceability 가이드

Specyn은 향후 dashboard, run history, reviewer audit 기능으로 확장할 수 있도록  
Agent 출력 자체에 가벼운 trace metadata를 남기는 방식을 권장합니다.

## 왜 필요한가요?

```text
agent output
  -> human-readable handoff
  -> machine-friendly trace hints
  -> future dashboard / audit / analytics reuse
```

지금은 단순 Markdown 출력이어도 괜찮지만, 필드가 일정하면 나중에 재구성하기 훨씬 쉬워집니다.

## 권장 필드

| 필드 | 설명 |
|---|---|
| `STEP_LABEL` | 단계 식별자 |
| `AGENT` | agent 이름 |
| `PHASE` | base / feedback |
| `FEEDBACK_ROUND` | 반복 라운드 번호 |
| `STATUS` | done / blocked / no-material-change |
| `CHANGED_FILES` | 실제 변경 파일 |
| `RESOLVED` | 해결된 항목 |
| `UNRESOLVED` | 미해결 이슈 |
| `BLOCKERS` | 즉시 중단 사유 |
| `NEXT_HANDOFF` | 다음 단계 전달사항 |

## 예시

```text
STEP_LABEL: 05-api-api-backend-contract-sync-r1
AGENT: api
PHASE: feedback
FEEDBACK_ROUND: 1
STATUS: done
CHANGED_FILES:
- specs/001-sample-service/api.md
RESOLVED:
- createUser 응답 모델 필드명을 userId로 통일
UNRESOLVED:
- 없음
BLOCKERS:
- 없음
NEXT_HANDOFF:
- Backend Agent는 응답 DTO와 OpenAPI 예시를 동일 명칭으로 맞춥니다.
```

## 작성 팁

- 라운드가 반복될수록 **달라진 점만 압축**해서 남기는 편이 좋습니다.
- `NO_MATERIAL_CHANGE` 상태면 추가 루프를 중단할 수 있게 설계하는 편이 좋습니다.
- 민감정보, 비밀키, 내부 토큰은 trace에 넣지 않는 편이 안전합니다.
