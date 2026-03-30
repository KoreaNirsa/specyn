# 12. Traceability Contract

Specyn은 향후 dashboard, run history, agent timeline, reviewer audit 기능으로 확장될 수 있도록
**Agent 출력 자체에 가벼운 trace metadata를 남기는 방식**을 권장한다.

## 왜 필요한가

```text
agent output
  -> human-readable handoff
  -> machine-friendly trace hints
  -> future dashboard / audit / analytics reuse
```

지금 당장은 단순 Markdown 출력이어도 괜찮지만, 아래 항목을 일관되게 남기면
나중에 별도 저장소나 DB 없이도 실행 이력을 재구성하기 쉬워진다.

## 권장 필드

| 필드 | 의미 | 예시 |
|---|---|---|
| `STEP_LABEL` | 현재 실행 단계 식별자 | `05-api-api-backend-contract-sync-r1` |
| `AGENT` | agent 이름 | `api` |
| `PHASE` | base 또는 feedback | `feedback` |
| `FEEDBACK_ROUND` | 피드백 라운드 번호 | `1` |
| `STATUS` | 종료 상태 | `done`, `blocked`, `no-material-change` |
| `CHANGED_FILES` | 실제 변경 파일 | `backend/...`, `specs/...` |
| `RESOLVED` | 이번 단계에서 해결된 항목 | contract mismatch 해결 |
| `UNRESOLVED` | 다음 단계로 넘길 미해결 이슈 | pagination naming 결정 필요 |
| `BLOCKERS` | 즉시 중단 사유 | destructive migration 승인 필요 |
| `NEXT_HANDOFF` | 다음 Agent가 바로 사용할 전달사항 | Backend가 DTO 명칭 반영 필요 |

## 권장 출력 예시

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
- Backend Agent는 응답 DTO와 OpenAPI 예시를 동일 명칭으로 맞춘다.
```

## 설계 원칙

- 사람이 바로 읽을 수 있어야 한다.
- 라운드가 반복될수록 **변경된 점만 압축**해서 남긴다.
- `NO_MATERIAL_CHANGE:` 상태면 추가 루프를 중단할 수 있어야 한다.
- 민감정보, 비밀키, 내부 토큰은 trace에 넣지 않는다.
- trace는 실행 로그를 대체하는 것이 아니라 **hardened handoff metadata** 역할을 한다.

## 메인테이너 체크포인트

- 새 Agent를 추가할 때 이 trace contract를 문서에 반영했는가
- prompt builder / prompt compiler / agent docs가 같은 필드 이름을 쓰는가
- dashboard 기능을 만들 때 기존 Markdown 산출물을 재사용할 수 있는가
