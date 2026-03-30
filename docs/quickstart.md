# 🚀 Quick Start

이 문서는 **처음 저장소를 받은 직후** 가장 실패 가능성이 낮은 경로로 Specyn을 확인하는 방법을 안내합니다.

## 먼저 알고 가시면 좋은 점

- 처음부터 전체 스택을 다 띄우지 않아도 괜찮습니다.
- `bootstrap → doctor → validate-spec → compile-prompts → run-sim` 순서가 가장 안전합니다.
- 이 경로는 Docker, 시스템 Gradle, OpenAI API Key 없이도 먼저 확인하실 수 있습니다.

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
  -> playbook 또는 architecture 문서로 이동
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
| `doctor` | Python, Node, Gradle, 포트, 환경 상태 점검 | 지금 어디까지 가능한지 알 수 있습니다. |
| `validate-spec` | 예제 spec bundle의 구조와 필수 항목 검증 | spec 작성 규칙이 지켜졌는지 확인합니다. |
| `compile-prompts` | spec를 agent prompt로 컴파일 | `.specyn/prompts/...`에 결과가 생성됩니다. |
| `run-sim` | backend 없이 로컬 시뮬레이션 실행 | 전체 흐름을 빠르게 감으로 익힐 수 있습니다. |

## 3) 이 단계에서 만들어지는 주요 결과물

| 경로 | 의미 |
|---|---|
| `.env` | 로컬 실행용 환경 변수 파일입니다. |
| `.venv` | Python 가상환경입니다. |
| `.specyn/prompts` | 컴파일된 prompt 산출물입니다. |
| `.workspace` | 실행 대상 workspace 기본 경로입니다. |
| `specs/projects` | 새 spec bundle을 만들 때 사용하는 프로젝트 경로입니다. |

## 4) 전체 스택이 필요할 때

기본 검증 경로가 잘 되었다면 그다음에 전체 스택을 확인해 보시면 됩니다.

### Linux / macOS

```bash
make bootstrap
make doctor
make dev
```

### Windows (PowerShell)

```powershell
python scripts/specyn_tasks.py bootstrap
python scripts/specyn_tasks.py doctor
python scripts/specyn_tasks.py dev
```

`doctor` 결과에서 `gradle.available=true`가 보이면 backend 포함 로컬 실행 준비가 된 상태라고 보시면 됩니다.

## 5) Docker Compose로 확인하고 싶을 때

```bash
docker compose -f docker-compose.local.yml up --build
```

Docker 경로는 로컬 설치 차이를 줄이고 싶을 때 특히 편합니다.

## 6) 새 spec bundle을 직접 만들어 보고 싶을 때

### Linux / macOS

```bash
python3 specyn.py init-spec --project-id sample-service --output-dir specs/projects/sample-service
```

### Windows (PowerShell)

```powershell
python specyn.py init-spec `
  --project-id sample-service `
  --output-dir specs/projects/sample-service
```

생성한 뒤에는 아래처럼 검증하시면 됩니다.

### Linux / macOS

```bash
python3 specyn.py validate --spec-dir specs/projects/sample-service
```

### Windows (PowerShell)

```powershell
python specyn.py validate --spec-dir specs/projects/sample-service
```

## 7) 다음으로 읽으면 좋은 문서

- 적용 시나리오별 흐름: [playbook.md](playbook.md)
- 구조 이해: [architecture.md](architecture.md)
- Agent 역할 이해: [agent-catalog.md](agent-catalog.md)
- spec 작성 기준: [sdd-principles.md](sdd-principles.md)
- 실행이 막힐 때: [troubleshooting.md](troubleshooting.md)
