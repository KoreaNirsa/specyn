# 🧭 적용 플레이북

이 문서는 Specyn을 **학습용으로 가볍게 확인하는 경우**부터 **현업에 맞게 확장하는 경우**까지 단계별로 정리한 플레이북입니다.

## 어떤 플레이북을 선택하면 좋을까요?

| 단계 | 추천 대상 | 목표 | 핵심 결과 |
|---|---|---|---|
| 초급 | 흐름을 이해하고 싶은 분 | spec → prompt → simulation 흐름 익히기 | 예제 bundle 이해 |
| 중급 | 내 프로젝트로 바꿔 보고 싶은 팀 | 새 spec bundle 작성과 실행 흐름 맞춤화 | 프로젝트별 spec bundle |
| 고급 | 현업에 붙이려는 팀 | 실행기, 운영 정책, trace, review gate 확장 | production-ready 운영 기준 |

## 전체 흐름 한눈에 보기

```text
초급
  -> 예제 bundle 검증
  -> prompt 생성
  -> 시뮬레이션

중급
  -> 새 spec bundle 생성
  -> agent/feedback loop 조정
  -> validate / compile / run

고급
  -> Codex / RAG / CI / trace / queue 확장
  -> 조직 정책과 human review gate 결합
```

## 1. 초급 플레이북

### 추천 상황

- 구조를 먼저 이해하고 싶은 경우
- 강의/스터디/사내 파일럿처럼 빠르게 흐름을 보여줘야 하는 경우
- 아직 OpenAI API Key나 Docker를 붙이고 싶지 않은 경우

### 권장 순서

1. `bootstrap`
2. `doctor`
3. `validate-spec`
4. `compile-prompts`
5. `run-sim`
6. 예제 spec와 prompt 산출물을 직접 읽어보기

### 여기서 꼭 확인해 보시면 좋은 것

| 확인 포인트 | 왜 중요한가요? |
|---|---|
| `specs/examples/todo-service` | core spec bundle이 어떤 모양인지 바로 볼 수 있습니다. |
| `.specyn/prompts/...` | spec가 agent prompt로 어떻게 바뀌는지 확인할 수 있습니다. |
| `agent.md` | Agent 실행 순서와 feedback loop의 source of truth가 됩니다. |
| `run-sim` 결과 | backend 없이도 전체 흐름을 이해하는 데 도움이 됩니다. |

## 2. 중급 플레이북

### 추천 상황

- 예제 Todo가 아니라 내 서비스 아이디어로 바꿔 보고 싶은 경우
- Backend/API/UI 책임을 분리해서 설계하고 싶은 경우
- 팀 내에서 spec-first 협업 규칙을 시험해 보고 싶은 경우

### 권장 순서

1. 새 spec bundle 생성
2. `product.md`부터 작성
3. `api.md`, `test.md`, `review.md` 작성
4. `agent.md`에서 실행 흐름과 feedback loop 선택
5. `validate`
6. `compile-prompts`
7. `run --workspace ...`

### 예시 명령

#### Linux / macOS

```bash
python3 specyn.py init-spec --project-id sample-service --output-dir specs/projects/sample-service

python3 specyn.py validate --spec-dir specs/projects/sample-service
python3 specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
```

#### Windows (PowerShell)

```powershell
python specyn.py init-spec `
  --project-id sample-service `
  --output-dir specs/projects/sample-service

python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts `
  --spec-dir specs/projects/sample-service `
  --output-dir .specyn/prompts/sample-service `
  --workspace .workspace/sample-service
```

### 중급 단계에서 자주 쓰는 설계 팁

| 주제 | 권장 사항 |
|---|---|
| spec 작성 순서 | `product.md`를 먼저 고정하면 downstream drift가 줄어듭니다. |
| 구조 규약 | `api.md`에 Spring Boot `global/common/domain`, FastAPI `app/global/common/domain` 힌트를 함께 적어두는 편이 좋습니다. |
| agent 선택 | 처음부터 모든 Agent를 켜기보다 core quality gate를 우선 유지하는 편이 안정적입니다. |
| feedback loop | API↔Backend, Design↔Frontend처럼 필요한 경계만 제한적으로 두는 편이 좋습니다. |

## 3. 고급 플레이북

### 추천 상황

- 실제 조직의 개발 프로세스에 붙이려는 경우
- Agent 실행 이력, trace, review gate, artifact 관리가 필요한 경우
- 온프레미스 / Kubernetes / Queue 기반 구조까지 확장하려는 경우

### 권장 순서

1. Codex CLI 연동
2. 팀 문서를 RAG 대상으로 편입
3. artifact 저장 정책 수립
4. CI에 spec validation + review gate 추가
5. trace metadata와 감사 추적 기준 정리
6. queue/worker 구조로 비동기화 검토

### 현업 적용 체크포인트

| 구분 | 질문 |
|---|---|
| 보안 | secret, token, 내부 경로가 prompt/log에 노출되지 않도록 설계했나요? |
| 실행 격리 | workspace를 프로젝트/런 단위로 분리했나요? |
| 품질 게이트 | test/review/docs/final-review 단계가 실제로 남아 있나요? |
| 감사 추적 | 누가 어떤 spec로 어떤 결과를 만들었는지 재구성할 수 있나요? |
| 롤백 | destructive change 발생 시 중단 기준과 복구 경로가 있나요? |

## 4. 상황별 권장 조합

| 상황 | 권장 Agent 조합 | 메모 |
|---|---|---|
| 백엔드 API 중심 서비스 | planner, api, backend, security, test, review, docs, final-review | frontend/design은 최소화할 수 있습니다. |
| 풀스택 서비스 | planner, design, api, backend, frontend, dba, devops, test, review, docs, final-review | 기본 예제 흐름과 가장 가깝습니다. |
| 사내 AX Builder | planner, rag, api, backend, devops, docs, final-review | RAG와 운영 정책의 비중이 커집니다. |
| 초기 파일럿 | planner, api, backend, test, docs | 최소 구성으로 시작해도 됩니다. |

## 5. 이 문서 다음에 무엇을 보면 좋을까요?

- spec 작성 기준을 더 자세히 보고 싶다면 [sdd-principles.md](sdd-principles.md)
- Agent 역할을 자세히 보고 싶다면 [agent-catalog.md](agent-catalog.md)
- 운영 관점이 필요하다면 [operations.md](operations.md)
- 메인테이너 관점까지 확장하려면 [../guide/maintainer.md](../guide/maintainer.md)
