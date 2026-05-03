# 🧩 Agent 카탈로그 및 실행 흐름

Specyn은 고정 파이프라인이 아니라 **`plan.md`를 기준으로 조립되는 실행 그래프**를 사용합니다.

## 1. 기본 실행 흐름

```text
Planner
  -> Design
  -> API
  -> Backend
  -> Frontend
  -> DBA
  -> DevOps
  -> Test
  -> Code Analysis
  -> Security
  -> Performance
  -> Review
  -> Docs
  -> Final Review
```

필요하면 `RAG`를 Planner 뒤에 붙여 근거 문서를 보강할 수 있습니다.

## 2. 대표 feedback loop 예시

```text
Backend 완료 후   -> API <-> Backend
Frontend 완료 후 -> Design <-> Frontend
DBA 완료 후      -> Backend <-> DBA
Docs 완료 후     -> Review <-> Docs
```

핵심은 **모든 Agent를 무한 반복하지 않고, 필요한 경계만 bounded loop로 재실행**한다는 점입니다.

## 3. Agent 분류표

| 분류 | Agent | 주요 책임 | 정의 문서 |
|---|---|---|---|
| 기획/설계 | Planner | 제품 목표, 범위, 시나리오, NFR 정규화 | [planner-agent.md](../agents/planner-agent.md) |
| 기획/설계 | Design | 사용자 흐름, 화면 구조, 상태, 접근성 설계 | [design-agent.md](../agents/design-agent.md) |
| 제어 | Orchestrator | 실행 순서, stop/retry 정책, validation ownership 관리 | [orchestrator-agent.md](../agents/orchestrator-agent.md) |
| 보조 | RAG | 내부 문서 근거 검색 및 요약 | [rag-agent.md](../agents/rag-agent.md) |
| 계약 | API | endpoint, schema, error contract 정리 | [api-agent.md](../agents/api-agent.md) |
| 구현 | Backend | Spring Boot / FastAPI 구현 경계와 코드 방향 정의 | [backend-agent.md](../agents/backend-agent.md) |
| 구현 | Frontend | React UI, 상태 관리, 사용자 피드백 처리 | [frontend-agent.md](../agents/frontend-agent.md) |
| 구현 | DBA | 스키마, 인덱스, 마이그레이션, 데이터 정합성 검토 | [dba-agent.md](../agents/dba-agent.md) |
| 구현 | DevOps | Docker, CI, 환경 변수, 관측성 기준 정리 | [devops-agent.md](../agents/devops-agent.md) |
| 검증 | Test | 자동화 테스트, QA 시나리오, coverage 기준 | [test-agent.md](../agents/test-agent.md) |
| 검증 | Code Analysis | 복잡도, 결합도, 유지보수성, 잠재 리스크 분석 | [code-analysis-agent.md](../agents/code-analysis-agent.md) |
| 검증 | Security | 입력 검증, 예외 노출, 비밀정보/권한 경계 검토 | [security-agent.md](../agents/security-agent.md) |
| 검증 | Performance | 병목, 지표, 최적화 포인트 검토 | [performance-agent.md](../agents/performance-agent.md) |
| 검증 | Review | blocker/major/minor 기준의 기술 리뷰 | [review-agent.md](../agents/review-agent.md) |
| 문서 | Docs | README/OpenAPI/운영 문서 동기화 | [docs-agent.md](../agents/docs-agent.md) |
| 최종 승인 | Final Review | 출시 가능 여부 판단 및 남은 리스크 정리 | [final-review-agent.md](../agents/final-review-agent.md) |

## 4. 어떤 Agent는 꼭 유지하는 편이 좋을까요?

| 상황 | 유지 권장 Agent |
|---|---|
| 최소 파일럿 | planner, api, backend, test, docs |
| 현업 적용 | planner, api, test, review, docs, final-review |
| 풀스택 프로젝트 | planner, design, api, backend, frontend, dba, devops, test, review, docs, final-review |

## 5. handoff 품질을 높이는 포인트

좋은 handoff는 다음 Agent가 아래를 즉시 이해할 수 있어야 합니다.

- 무엇이 완료되었는가
- 무엇이 검증되었는가
- 무엇이 아직 남아 있는가
- 어떤 파일과 규칙을 바로 봐야 하는가

그래서 Agent 출력에는 아래 정보가 있으면 좋습니다.

| 필드 | 의미 |
|---|---|
| `STEP_LABEL` | 현재 단계 식별자 |
| `PHASE` | base / feedback |
| `FEEDBACK_ROUND` | 반복 라운드 번호 |
| `STATUS` | done / blocked / no-material-change |
| `CHANGED_FILES` | 실제 변경 파일 목록 |
| `NEXT_HANDOFF` | 다음 Agent가 바로 사용할 전달사항 |

Trace 형식은 [../guide/traceability.md](../guide/traceability.md)에서 더 자세히 보실 수 있습니다.

## 6. Agent 설계 팁

| 주제 | 팁 |
|---|---|
| Agent 수 | 많을수록 좋은 것이 아니라 책임 경계가 명확해야 좋습니다. |
| loop 설계 | 반드시 `max_feedback_rounds` 같은 상한을 두는 편이 안전합니다. |
| RAG 사용 | 기본 흐름을 대체하기보다 근거 보강 수단으로 쓰는 편이 안정적입니다. |
| 문서 동기화 | Docs Agent를 흐름 끝에 두면 README/OpenAPI/운영 문서 drift를 줄이기 좋습니다. |

## 7. 함께 보면 좋은 문서

- 실행 흐름 전반: [architecture.md](architecture.md)
- spec 작성 기준: [sdd-principles.md](sdd-principles.md)
- 운영 관점: [operations.md](operations.md)
