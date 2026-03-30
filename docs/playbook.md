# 🧭 적용 플레이북

이 문서는 Specyn을 **학습용으로 가볍게 확인하는 단계**부터 **실제 spec bundle을 작성하고 전체 SDD를 끝까지 실행하는 단계**까지 순서대로 설명합니다.

핵심은 아래 두 가지 실행 모드를 구분해서 사용하는 것입니다.

| 실행 모드 | 언제 쓰나요? | 결과물 반영 방식 |
|---|---|---|
| 로컬 CLI 런타임(`specyn run`) | spec → prompt → 코드 산출 흐름을 빠르게 검증하고 싶을 때 | 저장소의 `frontend`, `backend`, `ai-server`, `docs`에 deterministic 산출물을 직접 생성 |
| Backend + AI Server + Codex | 실제 LLM/Codex 기반으로 patch/file 생성까지 연결하고 싶을 때 | `--workspace` 경로를 기준으로 Codex가 실제 파일 수정 |

---

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

### 꼭 확인하면 좋은 포인트

| 확인 포인트 | 왜 중요한가요? |
|---|---|
| `specs/examples/todo-service` | 최소 spec bundle이 어떤 모양인지 바로 볼 수 있습니다. |
| `specs/projects/sample-service` | `compile-prompts` 이후 실제 `run`까지 이어지는 fuller example bundle입니다. |
| `.specyn/prompts/...` | spec가 agent prompt로 어떻게 바뀌는지 확인할 수 있습니다. |
| `agent.md` | Agent 실행 순서와 feedback loop의 source of truth가 됩니다. |
| `run-sim` 결과 | backend 없이도 전체 흐름을 이해하는 데 도움이 됩니다. |

---

## 2. 중급 플레이북: `compile-prompts` 다음에 바로 전체 SDD 실행

이 단계가 현재 프로젝트의 핵심입니다.

이미 아래 명령까지 실행한 상태라면,

```powershell
python specyn.py compile-prompts `
  --spec-dir specs/projects/sample-service `
  --output-dir .specyn/prompts/sample-service `
  --workspace .workspace/sample-service
```

다음 단계는 **`specyn run`으로 실제 산출물을 저장소에 생성하는 것**입니다.

### 2-1. 어떤 Agent가 참여할지 정하는 방법

`specs/projects/sample-service/agent.md`의 front matter가 실행 흐름의 source of truth입니다.

- `execution_flow`: 기본 1차 실행 순서
- `feedback_loops`: bounded feedback loop
- `max_feedback_rounds`: loop 반복 상한
- `optional_agents`: 선택 Agent 목록
- `supported_agents`: 허용 Agent 목록

예를 들어 현재 예제는 아래 흐름을 사용합니다.

```text
planner -> design -> api -> backend -> frontend -> dba -> devops -> test -> code-analysis -> security -> performance -> review -> docs -> final-review
```

그리고 다음 bounded feedback loop를 가집니다.

- backend 이후 `api -> backend`
- frontend 이후 `design -> frontend`
- dba 이후 `backend -> dba`
- docs 이후 `review -> docs`

즉, “어떤 에이전트들이 프로젝트에 참여할지”는 `agent.md`만 수정하면 됩니다.

### 2-2. 스펙 문법 검증

`specyn validate`는 아래를 함께 검사합니다.

- 필수 spec 존재 여부 (`product/api/test/review/agent`)
- 필수 섹션 존재 여부 (`목적/입력/출력/실행 규칙/Validation 기준/Prompt`)
- `Prompt`의 RIF(Role / Instructions / Format) 구조
- `agent.md`의 실행 흐름, 필수 agent, feedback loop 순서, 중복 여부
- `product.md`의 핵심 시나리오/NFR/제외 범위
- `api.md`의 엔드포인트 표, Request/Response 예시, 오류 정책
- `test.md`의 테스트 시나리오 수
- `review.md`의 구조/보안/테스트/운영 규칙 수

#### Linux / macOS

```bash
python3 specyn.py validate --spec-dir specs/projects/sample-service
```

#### Windows (PowerShell)

```powershell
python specyn.py validate --spec-dir specs/projects/sample-service
```

### 2-3. 로컬 CLI 런타임으로 전체 SDD 실행

이 모드는 **추가 인프라 없이** 가장 안정적으로 끝까지 확인하는 경로입니다.

#### Linux / macOS

```bash
python3 specyn.py run \
  --spec-dir specs/projects/sample-service \
  --project-id sample-service \
  --workspace .workspace/sample-service
```

#### Windows (PowerShell)

```powershell
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service
```

### 2-4. 이 명령이 실제로 만드는 것

`specyn run`의 기본 로컬 런타임은 아래 파일들을 **저장소에 직접 생성/갱신**합니다.

| Agent | 대표 산출물 |
|---|---|
| API | `docs/openapi/<project>.yaml`, `frontend/src/generated/<project>/apiContract.ts` |
| Backend | `backend/src/main/java/.../generated/...Controller.java`, `ai-server/app/generated/<project>/router.py` |
| Frontend | `frontend/src/generated/<project>/GeneratedProjectPage.tsx` |
| DBA | `backend/src/main/resources/db/generated/<project>.sql` |
| DevOps | `.specyn/generated/<project>/docker-compose.generated.yml` |
| Test | `ai-server/tests/generated/test_<project>_generated_route.py`, `docs/generated/<project>-test-plan.md` |
| Docs | `docs/generated/<project>.md` |

또한 아래 보조 산출물도 함께 생성됩니다.

- `.specyn/prompts/<project>/...prompt.md`
- `.workspace/<project>/.specyn/runs/<run-id>/manifest.json`
- `.workspace/<project>/.specyn/runs/<run-id>/steps/*.md`

### 2-5. 생성 결과를 바로 확인하는 방법

`python scripts/specyn_tasks.py dev`로 전체 개발 서버를 띄운 뒤 아래를 확인합니다.

| 서비스 | 확인 주소 |
|---|---|
| Frontend generated route 목록 | `http://localhost:5173/generated` |
| Frontend generated page | `http://localhost:5173/generated/sample-service` |
| Backend generated summary | `http://localhost:8080/api/v1/generated/sample-service/summary` |
| AI Server generated context | `http://localhost:8000/generated/sample-service/context` |

즉, 스펙을 작성하고 `specyn run`을 실행하면 **frontend/backend/ai-server에 바로 코드가 생기고**, dev 서버에서 즉시 확인할 수 있습니다.

---

## 3. Codex 실행 환경 플레이북

이 모드는 실제 Codex CLI를 통해 patch/file 생성을 수행하려는 경우에 사용합니다.

### 3-1. 준비

1. `.env` 또는 셸 환경에 Codex 실행 모드 설정
2. AI Server / Backend / Frontend 실행 (`python scripts/specyn_tasks.py dev`)
3. `specyn run --backend-url ...` 호출

### 3-2. 추천 환경 변수

#### Linux / macOS

```bash
export CODEX_EXEC_MODE=cli
export CODEX_COMMAND_TEMPLATE='codex exec --json --cwd {workspace}'
```

#### Windows (PowerShell)

```powershell
$env:CODEX_EXEC_MODE = "cli"
$env:CODEX_COMMAND_TEMPLATE = "codex exec --json --cwd {workspace}"
```

### 3-3. 현재 저장소에 바로 반영하고 싶을 때

Codex가 실제 파일을 현재 저장소에 쓰게 하려면 `--workspace .` 를 사용합니다.

#### Linux / macOS

```bash
python3 specyn.py run \
  --backend-url http://localhost:8080 \
  --spec-dir specs/projects/sample-service \
  --project-id sample-service \
  --workspace .
```

#### Windows (PowerShell)

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .
```

### 3-4. 안전한 격리 workspace에 반영하고 싶을 때

실패 복구와 비교가 더 중요하다면 별도 workspace를 사용합니다.

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service-codex
```

### 3-5. 로컬 CLI 런타임과 Codex 모드의 차이

| 구분 | 로컬 CLI 런타임 | Backend + Codex |
|---|---|---|
| 목적 | deterministic scaffold 생성 | 실제 LLM/Codex 기반 코드 수정 |
| 의존성 | Python만 있으면 됨 | Backend + AI Server + Codex CLI 필요 |
| 파일 반영 | 저장소에 즉시 생성 | `--workspace` 위치에 Codex가 반영 |
| 재현성 | 높음 | 모델/프롬프트/환경에 영향 받음 |
| 추천 용도 | 구조 검증, 초기 scaffold, 데모 | 실제 patch 생성, 반복 수정, 사람 검토와 결합 |

---

## 4. 상황별 권장 조합

| 상황 | 권장 Agent 조합 | 메모 |
|---|---|---|
| 백엔드 API 중심 서비스 | planner, api, backend, security, test, review, docs, final-review | frontend/design은 최소화할 수 있습니다. |
| 풀스택 서비스 | planner, design, api, backend, frontend, dba, devops, test, review, docs, final-review | 현재 sample-service 흐름과 가장 가깝습니다. |
| 사내 AX Builder | planner, rag, api, backend, devops, docs, final-review | RAG와 운영 정책의 비중이 커집니다. |
| 초기 파일럿 | planner, api, backend, test, docs | 최소 구성으로 시작해도 됩니다. |

---

## 5. 이 문서 다음에 무엇을 보면 좋을까요?

- spec 작성 기준을 더 자세히 보고 싶다면 [sdd-principles.md](sdd-principles.md)
- Agent 역할을 자세히 보고 싶다면 [agent-catalog.md](agent-catalog.md)
- Codex 환경을 자세히 보고 싶다면 [04-codex-execution.md](04-codex-execution.md)
- 로컬 기동과 health check를 보려면 [../guide/local-development.md](../guide/local-development.md)
