# 03. Agent Flow

## 기본 개념

Specyn은 고정 파이프라인이 아니라 **`agent.md` 기반 실행 그래프**를 사용한다.
`execution_flow`는 기본 1차 실행 순서를, `feedback_loops`는 반복 협업이 필요한 Agent 재진입 순서를 정의한다.

```text
base execution_flow
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

bounded feedback_loops
  Backend 완료 후     : API <-> Backend
  Frontend 완료 후   : Design <-> Frontend
  DBA 완료 후        : Backend <-> DBA
  Docs 완료 후       : Review <-> Docs
```

## 권장 기본 흐름

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

## 반복 피드백을 포함한 실행 예시

`max_feedback_rounds: 1`인 경우 예제 bundle의 실제 실행 계획은 아래처럼 확장된다.

```text
Planner
  -> Design
  -> API
  -> Backend
  -> API
  -> Backend
  -> Frontend
  -> Design
  -> Frontend
  -> DBA
  -> Backend
  -> DBA
  -> DevOps
  -> Test
  -> Code Analysis
  -> Security
  -> Performance
  -> Review
  -> Docs
  -> Review
  -> Docs
  -> Final Review
```

핵심은 **모든 Agent를 무한 반복시키는 것이 아니라, 필요한 지점만 bounded loop로 재실행**한다는 점이다.

## RAG를 함께 쓰는 경우

```text
Planner
  -> RAG
  -> Design / API / Review / Docs 지원
```

RAG는 기본 흐름을 대체하지 않고 **근거 문서 보강** 용도로만 사용한다.

## 단계별 검증 포인트

| 단계 | 주요 책임 | 차단 조건 |
|---|---|---|
| Planner | 요구사항, 범위, NFR 정규화 | core spec 누락 |
| Design | 화면/상태/접근성 구조 | 핵심 사용자 흐름 불명확 |
| API | endpoint / schema / error contract | 계약 불명확 |
| Backend | Spring Boot / FastAPI 구현 | 구조/예외/검증 누락 |
| Frontend | UI, 상태, 피드백 | 빈/오류/로딩 상태 누락 |
| DBA | 스키마/인덱스/마이그레이션 | 파괴적 변경/정합성 위험 |
| DevOps | 컨테이너/CI/관측성/런타임 계약 | 비이식적 배포/운영 blocker |
| Test | 자동화 검증 | coverage 부족 / flaky risk |
| Code Analysis | 복잡도/유지보수성 | 잠재 버그/구조 악화 |
| Security | 입력/에러/비밀정보 경계 | 보안 blocker |
| Performance | 병목/지표/최적화 | NFR 위반 가능성 |
| Review | blocker/major/minor 분류 | release blocker 존재 |
| Docs | README/OpenAPI/운영 문서 | 구현과 문서 drift |
| Final Review | 출시 가능 여부 최종 판단 | must-fix 잔존 |

## feedback loop 설계 원칙

### 언제 loop를 두는가
- 계약(API)과 구현(Backend) 사이에 상호 보정이 필요한 경우
- UX 설계와 실제 화면 구현 사이에 상태/접근성 정합이 필요한 경우
- 영속성 설계와 구현 경계 사이에 정합성 보정이 필요한 경우
- Review 결과를 문서와 다시 동기화해야 하는 경우

### 언제 loop를 두지 않는가
- 단순 정보 전달만 필요한 경우
- 동일 Agent를 다시 실행해도 산출물 개선 여지가 없는 경우
- human approval 없이는 진행하면 안 되는 blocker인 경우

### 무한 반복 방지 규칙
- `max_feedback_rounds` 또는 각 loop의 `max_rounds`를 반드시 둔다.
- 같은 문제가 상한 라운드 이후에도 남으면 human review로 승격한다.
- `NO_MATERIAL_CHANGE:` 상태면 추가 루프를 중단한다.

## trace metadata 권장 사항

- handoff 상단에 `STEP_LABEL`, `PHASE`, `FEEDBACK_ROUND`, `STATUS`를 남기면 후속 Agent와 운영자가 흐름을 다시 구성하기 쉽다.
- `CHANGED_FILES`, `RESOLVED`, `UNRESOLVED`, `BLOCKERS`, `NEXT_HANDOFF`를 분리하면 bounded loop의 품질이 올라간다.
- 향후 dashboard / timeline 기능을 고려하면 field 이름을 프로젝트 내에서 일관되게 유지하는 편이 좋다.

## handoff 원칙

- 다음 Agent가 바로 사용할 수 있는 요약이어야 한다.
- validation 결과는 pass/fail 또는 blocker 여부가 분명해야 한다.
- patch가 필요하면 어느 파일을 어떻게 수정할지 방향을 남겨야 한다.
- feedback round에서는 **무엇이 바뀌었는지 / 왜 바뀌었는지 / 무엇이 그대로인지**를 분리해야 한다.
- review/security/performance 결과는 Final Review에서 다시 종합한다.

## 실무 팁

- 모든 프로젝트가 모든 agent를 다 사용할 필요는 없다.
- production 지향 프로젝트라면 DevOps agent를 포함해 런타임/배포/관측성 기준을 초기에 고정하는 편이 안전하다.
- 다만 `planner`, `api`, `test`, `review`, `docs`, `final-review`는 core quality gate로 유지하는 것을 권장한다.
- RAG는 planner/review/docs 품질을 올리는 보조 수단으로 쓰는 편이 안정적이다.
- feedback loop는 적을수록 좋고, 필요한 지점에만 명시적으로 둬야 유지보수가 쉽다.
