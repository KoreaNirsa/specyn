# 🚀 Quick Start

이 문서는 **처음 저장소를 받은 직후** 가장 실패 가능성이 낮은 경로로 Specyn을 확인하는 방법을 안내합니다.

## 먼저 알고 가시면 좋은 점

- 처음부터 전체 스택을 다 띄우지 않아도 괜찮습니다.
- `bootstrap → doctor → validate-spec → compile-prompts → run-sim` 순서가 가장 안전합니다.
- 그 다음 단계로는 `specyn run`을 사용해 **실제 저장소 산출물 생성**까지 바로 이어갈 수 있습니다.
- 현재 저장소에는 fuller example bundle로 `specs/projects/sample-service`가 포함되어 있습니다.

## 준비 사항

| 항목 | 필수 여부 | 권장 버전 | 설명 |
|---|---|---|---|
| Python | 필수 | 3.12+ | task runner와 CLI 실행에 사용합니다. |
| Node.js / npm | 필수 | 20+ | 프런트엔드 의존성과 일부 bootstrap 단계에 필요합니다. |
| Gradle | 선택 | 8.14+ | repo-local Gradle 준비가 실패하는 환경에서 필요합니다. |
| Docker | 선택 | 최신 | 전체 스택을 Compose로 띄울 때 필요합니다. |
| OpenAI API Key | 선택 | - | 실제 AI 실행/Codex 연동 시 필요합니다. |

## 추천 흐름 한눈에 보기

```text
환경 준비
  -> bootstrap
  -> doctor
  -> validate-spec
  -> compile-prompts
  -> run-sim
  -> specyn run (로컬 CLI 런타임)
  -> dev 서버에서 생성 결과 확인
```

## 1) 기본 검증 경로

### Linux / macOS

```bash
cp .env.example .env
make bootstrap
make doctor
make validate-spec
make compile-prompts
make run-sim
```

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
python scripts/specyn_tasks.py bootstrap
python scripts/specyn_tasks.py doctor
python scripts/specyn_tasks.py validate-spec
python scripts/specyn_tasks.py compile-prompts
python scripts/specyn_tasks.py run-sim
```

## 2) 각 명령이 하는 일

| 명령 | 무엇을 확인하나요? | 기대 결과 |
|---|---|---|
| `bootstrap` | `.venv`, 프런트엔드 의존성, 로컬 작업 폴더 준비 | 실행 준비가 됩니다. |
| `doctor` | Python, Node, Gradle, 환경 상태 점검 | 지금 어디까지 가능한지 알 수 있습니다. |
| `validate-spec` | 예제 spec bundle의 구조와 필수 항목 검증 | spec 작성 규칙이 지켜졌는지 확인합니다. |
| `compile-prompts` | spec를 agent prompt로 컴파일 | `.specyn/prompts/...`에 결과가 생성됩니다. |
| `run-sim` | backend 없이 로컬 시뮬레이션 실행 | 전체 흐름을 빠르게 감으로 익힐 수 있습니다. |

## 3) `compile-prompts` 다음 단계: 실제 산출물 생성

### Linux / macOS

```bash
python3 specyn.py run \
  --spec-dir specs/projects/sample-service \
  --project-id sample-service \
  --workspace .workspace/sample-service
```

### Windows (PowerShell)

```powershell
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service
```

이 명령은 아래 파일을 실제로 생성합니다.

- `frontend/src/generated/sample-service/GeneratedProjectPage.tsx`
- `frontend/src/generated/sample-service/apiContract.ts`
- `backend/src/main/java/com/axbuilder/backend/generated/sample_service/GeneratedSampleServiceController.java`
- `ai-server/app/generated/sample_service/router.py`
- `docs/openapi/sample-service.yaml`
- `docs/generated/sample-service.md`

## 4) 생성 결과를 바로 보고 싶을 때

### Linux / macOS

```bash
make dev
```

### Windows (PowerShell)

```powershell
python scripts/specyn_tasks.py dev
```

브라우저에서 아래 주소를 확인합니다.

- `http://localhost:5173/generated`
- `http://localhost:5173/generated/sample-service`
- `http://localhost:8080/api/v1/generated/sample-service/summary`
- `http://localhost:8000/generated/sample-service/context`

## 5) 각 단계에서 만들어지는 주요 결과물

| 경로 | 의미 |
|---|---|
| `.env` | 로컬 실행용 환경 변수 파일입니다. |
| `.venv` | Python 가상환경입니다. |
| `.specyn/prompts` | 컴파일된 prompt 산출물입니다. |
| `.workspace/<project>/.specyn/runs` | run manifest와 step report가 쌓이는 위치입니다. |
| `specs/projects/sample-service` | fuller example bundle입니다. |
| `frontend/src/generated` | generated frontend page/contract가 생기는 위치입니다. |
| `backend/src/main/java/.../generated` | generated Spring Boot controller가 생기는 위치입니다. |
| `ai-server/app/generated` | generated FastAPI route가 생기는 위치입니다. |

## 6) Codex까지 연결하고 싶을 때

전체 스택을 띄운 뒤 아래처럼 Backend 경유 모드로 실행합니다.

```powershell
$env:CODEX_EXEC_MODE = "cli"
$env:CODEX_COMMAND_TEMPLATE = "codex exec --json --cwd {workspace}"
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .
```

`--workspace .` 는 Codex가 현재 저장소를 직접 수정하게 하는 설정입니다.

## 7) 다음으로 읽으면 좋은 문서

- 실행 단계별 플레이북: [playbook.md](playbook.md)
- Codex 실행 환경: [04-codex-execution.md](04-codex-execution.md)
- 구조 이해: [architecture.md](architecture.md)
- Agent 역할 이해: [agent-catalog.md](agent-catalog.md)
- spec 작성 기준: [sdd-principles.md](sdd-principles.md)
- 실행이 막힐 때: [troubleshooting.md](troubleshooting.md)
