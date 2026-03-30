# 🧭 적용 플레이북

이 문서는 **현재 playbook 에서 `compile-prompts` 명령까지 실행한 뒤 다음에 무엇을 해야 하는지**를 중심으로 정리합니다.

핵심 질문은 두 가지입니다.

1. `compile-prompts` 다음에 `specyn.py run` 을 어떻게 실행하는가?
2. CLI 기반 로컬 런타임과 Codex 실행 환경은 어떻게 다른가?

## 1. `compile-prompts` 이후 바로 이어지는 단계

이미 아래 명령까지 실행했다면,

```powershell
python specyn.py compile-prompts `
  --spec-dir specs/projects/sample-service `
  --output-dir .specyn/prompts/sample-service `
  --workspace .workspace/sample-service
```

다음 단계는 `specyn.py run` 입니다.

```powershell
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service
```

이 명령은 단순 시뮬레이션이 아니라, **저장소에 실제 frontend/backend/ai-server/docs 산출물을 생성**합니다.

## 2. 어떤 Agent 가 참여하는가?

프로젝트에 참여하는 Agent 는 `specs/projects/sample-service/agent.md` 가 결정합니다.

중요한 필드:

- `execution_flow`: 기본 실행 순서
- `feedback_loops`: bounded feedback loop
- `max_feedback_rounds`: 피드백 반복 상한
- `supported_agents`: 허용 Agent 목록
- `optional_agents`: 선택 Agent 목록

현재 sample-service 의 기본 흐름:

```text
planner -> design -> api -> backend -> frontend -> dba -> devops -> test -> code-analysis -> security -> performance -> review -> docs -> final-review
```

즉, **어떤 에이전트들이 프로젝트에 참여할지 정하는 곳은 `agent.md`** 입니다.

## 3. 스펙 문법 검사는 어디서 하나?

`specyn.py validate` 가 담당합니다.

```powershell
python specyn.py validate --spec-dir specs/projects/sample-service
```

검사 대상 예시:

- 필수 spec 존재 여부 (`product/api/test/review/agent`)
- 필수 섹션 존재 여부
- Prompt 의 RIF 구조
- `agent.md` 의 execution flow / feedback loop 정합성
- `product.md` 의 핵심 시나리오 / NFR / 제외 범위
- `api.md` 의 endpoint 표 / request-response 예시 / 오류 정책
- `test.md` 의 테스트 시나리오
- `review.md` 의 구조/보안/테스트/운영 기준

## 4. CLI 기반 로컬 런타임

이 모드는 **추가 인프라 없이 가장 안정적으로 전체 흐름을 확인하는 경로**입니다.

### 실행 명령

```powershell
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service
```

### 특징

- deterministic scaffold 생성
- 저장소의 generated 경로에 산출물 반영
- 문서/샘플 데모/초기 구조 검증에 적합
- OpenAI API Key 없이도 실행 가능

### 생성되는 주요 파일

| 영역 | 대표 산출물 |
|---|---|
| Frontend | `frontend/src/generated/sample-service/GeneratedProjectPage.tsx` |
| Frontend contract | `frontend/src/generated/sample-service/apiContract.ts` |
| Backend | `backend/src/main/java/com/axbuilder/backend/generated/sample_service/GeneratedSampleServiceController.java` |
| AI Server | `ai-server/app/generated/sample_service/router.py` |
| Docs | `docs/generated/sample-service.md`, `docs/generated/sample-service-test-plan.md` |
| OpenAPI | `docs/openapi/sample-service.yaml` |
| Run trace | `.workspace/sample-service/.specyn/runs/<run-id>/...` |

### 실행 후 확인

```powershell
python scripts/specyn_tasks.py dev
```

확인 URL:

- `http://localhost:5173/generated`
- `http://localhost:5173/generated/sample-service`
- `http://localhost:8080/api/v1/generated/sample-service/summary`
- `http://localhost:8080/api/v1/tasks`
- `http://localhost:8000/generated/sample-service/context`

## 5. Codex 실행 환경

이 모드는 **Backend + AI Server + Codex CLI** 조합으로 실제 patch/file 생성을 수행할 때 사용합니다.

### 준비

```powershell
$env:CODEX_EXEC_MODE = "cli"
$env:CODEX_COMMAND_TEMPLATE = "codex exec --json --cwd {workspace}"
python scripts/specyn_tasks.py dev
```

### 현재 저장소에 직접 반영

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .
```

### 별도 workspace 에 반영

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service-codex
```

## 6. 어떤 모드를 먼저 써야 하나?

| 상황 | 권장 모드 |
|---|---|
| 저장소를 처음 실행해 본다 | CLI 기반 로컬 런타임 |
| 문서/샘플/구조가 올바른지 본다 | CLI 기반 로컬 런타임 |
| 실제 Codex patch 경로까지 실험한다 | Codex 실행 환경 |
| 사람이 검토 가능한 격리 workspace 가 필요하다 | Codex 실행 환경 + 별도 workspace |

## 7. 다음에 볼 문서

- `run` 옵션 상세: [cli-run-reference.md](cli-run-reference.md)
- sample-service spec 참고 가이드: [sample-service-reference.md](sample-service-reference.md)
- Codex 상세: [04-codex-execution.md](04-codex-execution.md)
- 로컬 개발 상세: [../guide/local-development.md](../guide/local-development.md)
