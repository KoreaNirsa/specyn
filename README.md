<p align="center">
  <img src="docs/assets/specyn-banner.svg" alt="Specyn banner" width="100%" />
</p>

<h1 align="center">🚀 Specyn</h1>

<p align="center">
  <a href="LICENSE"><img src="docs/assets/badge-license.svg" alt="Apache-2.0 License" /></a>
  <img src="docs/assets/badge-stack.svg" alt="Spring Boot · FastAPI · React" />
  <img src="docs/assets/badge-sdd.svg" alt="Spec Driven Development" />
  <img src="docs/assets/badge-ci.svg" alt="GitHub Actions Ready" />
</p>

**Specyn**은 스펙 번들에서 시작해 프롬프트, 에이전트 실행 흐름, 코드 산출물, 문서, 실행 확인까지 이어지는 **SDD(Spec Driven Development) 프레임워크**입니다.

이 저장소는 다음 두 경로를 모두 지원합니다.

1. **로컬 CLI 런타임**: `specyn.py run` 이 `frontend/backend/ai-server/docs` 산출물을 저장소에 직접 생성합니다.
2. **Codex 실행 환경**: Backend + AI Server + Codex CLI 조합으로 실제 patch/file 생성을 수행합니다.

현재 저장소에는 이 흐름을 끝까지 확인할 수 있는 **실행 가능한 샘플 CRUD 프로젝트** `specs/projects/sample-service` 가 포함되어 있습니다.

## 빠르게 이해하는 핵심 흐름

```text
spec bundle 작성/수정
  -> validate
  -> compile-prompts
  -> run
  -> dev
  -> /generated/sample-service 에서 실제 결과 확인
```

## 저장소 구조

```text
/specyn
├── backend                # Spring Boot 오케스트레이터
├── ai-server              # FastAPI + generated route + RAG helper
├── frontend               # React(Vite) UI
├── agents                 # Agent 정의서
├── specs                  # spec bundle 템플릿 및 예제
├── tools                  # CLI, validator, prompt compiler, local runtime
├── scripts                # bootstrap / doctor / dev task runner
├── docs                   # 도입, 실행, playbook 문서
├── guide                  # 운영, 유지보수, 확장 가이드
└── specyn.py              # CLI entrypoint
```

## 가장 추천하는 첫 실행 순서

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
python scripts/specyn_tasks.py bootstrap
python scripts/specyn_tasks.py doctor
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts `
  --spec-dir specs/projects/sample-service `
  --output-dir .specyn/prompts/sample-service `
  --workspace .workspace/sample-service
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service
python scripts/specyn_tasks.py dev
```

### Linux / macOS

```bash
cp .env.example .env
python3 scripts/specyn_tasks.py bootstrap
python3 scripts/specyn_tasks.py doctor
python3 specyn.py validate --spec-dir specs/projects/sample-service
python3 specyn.py compile-prompts \
  --spec-dir specs/projects/sample-service \
  --output-dir .specyn/prompts/sample-service \
  --workspace .workspace/sample-service
python3 specyn.py run \
  --spec-dir specs/projects/sample-service \
  --project-id sample-service \
  --workspace .workspace/sample-service
python3 scripts/specyn_tasks.py dev
```

## 위 흐름으로 실제 확인할 수 있는 것

`sample-service` 는 단순 placeholder가 아니라 **작업(Task) CRUD 웹사이트**를 확인하기 위한 샘플입니다.

`specyn.py run` 이후 생성되는 대표 산출물:

- `frontend/src/generated/sample-service/GeneratedProjectPage.tsx`
- `frontend/src/generated/sample-service/apiContract.ts`
- `backend/src/main/java/com/axbuilder/backend/generated/sample_service/GeneratedSampleServiceController.java`
- `ai-server/app/generated/sample_service/router.py`
- `docs/openapi/sample-service.yaml`
- `docs/generated/sample-service.md`

`python scripts/specyn_tasks.py dev` 이후 확인 주소:

- Frontend 목록: `http://localhost:5173/generated`
- 샘플 CRUD 페이지: `http://localhost:5173/generated/sample-service`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI Server context: `http://localhost:8000/generated/sample-service/context`
- Backend CRUD API: `http://localhost:8080/api/v1/tasks`

샘플 CRUD 페이지에서 아래를 바로 확인할 수 있습니다.

1. 새 작업 생성
2. 작업 목록/상세 조회
3. 상태 토글 (`PENDING` ↔ `DONE`)
4. 삭제
5. generated summary / API contract 확인

## `specyn.py run` 이 중요한 이유

`compile-prompts` 까지는 “어떤 에이전트에게 어떤 프롬프트가 갈지”를 확인하는 단계입니다.

그 다음 단계인 `specyn.py run` 이 실제로 아래를 수행합니다.

- `agent.md` 의 `execution_flow` / `feedback_loops` 해석
- spec bundle 기반 blueprint 생성
- frontend/backend/ai-server/docs 산출물 생성
- workspace run manifest와 step report 기록

즉, **playbook.md 에서 `compile-prompts` 다음에 이어지는 실제 실행 단계**가 바로 `specyn.py run` 입니다.

## Codex 실행 환경으로 확장할 때

Backend + AI Server + Codex CLI 를 함께 쓰려면 아래처럼 `--backend-url` 을 추가합니다.

```powershell
$env:CODEX_EXEC_MODE = "cli"
$env:CODEX_COMMAND_TEMPLATE = "codex exec --json --cwd {workspace}"

python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .
```

- `--workspace .` : 현재 저장소를 직접 수정
- `--workspace .workspace/sample-service-codex` : 별도 작업 디렉터리에서 검토

## 문서 읽기 순서

가장 빠른 경로:

1. [docs/quickstart.md](docs/quickstart.md)
2. [docs/playbook.md](docs/playbook.md)
3. [docs/cli-run-reference.md](docs/cli-run-reference.md)
4. [docs/sample-service-reference.md](docs/sample-service-reference.md)
5. [guide/local-development.md](guide/local-development.md)

문서 허브는 [docs/README.md](docs/README.md), 운영/유지보수 가이드는 [guide/README.md](guide/README.md) 에서 이어집니다.
