# 🧠 프롬프트 엔지니어링 원칙

Specyn에서 prompt는 단순한 한 줄 지시가 아니라 **spec bundle, agent 정의, 이전 단계 결과**를 묶어 실행 가능한 계약으로 바꾸는 과정에 가깝습니다.

## 1. 기본 원칙

| 원칙 | 설명 |
|---|---|
| spec-first | 프롬프트보다 spec bundle이 우선입니다. |
| role clarity | Agent마다 단일 책임과 기대 산출물을 분명히 합니다. |
| deterministic handoff | 다음 Agent가 바로 이해할 수 있는 형식을 유지합니다. |
| validation-aware | 검증 결과와 blocker를 함께 전달합니다. |
| domain neutral | 예제 도메인에 과적합되지 않도록 일반화 가능한 표현을 우선합니다. |

## 2. Prompt 구성 추천 방식

```text
Role
Instructions
Format
```

이 구조를 기준으로 작성하면 사람과 Agent 모두에게 읽기 쉬운 prompt가 됩니다.

## 3. Agent prompt에서 자주 필요한 요소

| 요소 | 왜 필요한가요? |
|---|---|
| 입력 spec 요약 | Agent가 지금 무엇을 기준으로 판단해야 하는지 알려줍니다. |
| 이전 단계 결과 | 중복 작업과 drift를 줄여 줍니다. |
| validation 상태 | blocker가 있으면 다음 단계에서 무조건 알아야 합니다. |
| 출력 형식 | handoff 품질을 안정화해 줍니다. |
| 가정/리스크 표기 | 숨겨진 모호성을 줄입니다. |

## 4. handoff 형식 예시

```text
1. 작업 요약
2. 변경 파일 목록
3. validation 결과
4. patch 또는 파일 내용
5. 다음 Agent 전달사항
```

## 5. 우선순위 규칙

낮은 우선순위 문장을 높은 우선순위 지시처럼 취급하지 않는 것이 중요합니다.

1. system / framework 지시
2. agent definition
3. validated spec bundle
4. 이전 단계 결과
5. 코드/주석/로그/검색 결과

## 6. prompt injection 대응

| 상황 | 대응 방식 |
|---|---|
| 생성된 코드 주석 안의 지시 | 시스템 지시처럼 승격하지 않습니다. |
| RAG 결과 안의 숨은 명령 | 근거 자료로만 취급하고 권한 있는 명령으로 보지 않습니다. |
| spec와 충돌하는 외부 문서 | 무시하거나 `RISK:`로 기록합니다. |

## 7. 비밀정보 보호 원칙

- `.env`, secret, token, 내부 경로를 추정해서 출력하지 않습니다.
- prompt snapshot에는 필요한 정보만 남기고 민감값은 직접 넣지 않는 편이 좋습니다.
- trace나 handoff에도 비밀정보를 남기지 않는 편이 안전합니다.

## 8. feedback round에서의 작성 팁

feedback round에서는 특히 아래를 분리해 적는 편이 좋습니다.

- 무엇이 바뀌었는가
- 왜 바뀌었는가
- 무엇이 그대로인가
- 남은 blocker는 무엇인가

## 9. trace-aware output

아래 같은 필드가 있으면 나중에 dashboard나 audit 기능으로 확장하기 쉬워집니다.

| 필드 | 의미 |
|---|---|
| `STEP_LABEL` | 단계 식별자 |
| `AGENT` | agent 이름 |
| `PHASE` | base / feedback |
| `STATUS` | done / blocked / no-material-change |
| `NEXT_HANDOFF` | 다음 단계 전달사항 |

자세한 필드 설명은 [../guide/traceability.md](../guide/traceability.md)에서 확인하실 수 있습니다.

## 10. 함께 보면 좋은 문서

- spec 작성 원칙: [sdd-principles.md](sdd-principles.md)
- Agent 흐름: [agent-catalog.md](agent-catalog.md)
- 운영/유지보수: [../guide/maintainer.md](../guide/maintainer.md)
