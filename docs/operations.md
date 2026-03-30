# ⚙️ 운영 및 실행 가이드

이 문서는 Specyn을 어떤 모드로 실행할 수 있는지, 환경 변수는 무엇을 의미하는지, CI는 무엇을 검증하는지 정리합니다.

## 1. 실행 모드 비교

| 모드 | 대표 명령 | 준비물 | 추천 상황 |
|---|---|---|---|
| 기본 검증 모드 | `make validate-spec`, `make compile-prompts`, `make run-sim` | Python, Node | 저장소를 처음 확인할 때 |
| 로컬 네이티브 모드 | `make dev` | Python, Node, Gradle(또는 repo-local Gradle) | 서비스별 개발/통합 테스트 |
| 부분 실행 모드 | `make ai-server`, `make backend`, `make frontend` | 해당 런타임 | 특정 계층만 집중해서 볼 때 |
| Docker Compose 모드 | `docker compose -f docker-compose.local.yml up --build` | Docker | 설치 차이를 줄이고 싶을 때 |

## 2. 가장 안전한 운영 순서

```text
bootstrap
  -> doctor
  -> validate-spec
  -> compile-prompts
  -> run-sim
  -> dev 또는 docker compose
```

## 3. 자주 쓰는 명령 정리

| 명령 | 설명 |
|---|---|
| `make bootstrap` | Python/Frontend 의존성과 로컬 작업 폴더를 준비합니다. |
| `make doctor` | 실행 가능 상태를 진단합니다. |
| `make validate-spec` | 예제 spec bundle의 유효성을 검사합니다. |
| `make compile-prompts` | 예제 bundle에서 prompt 파일을 만듭니다. |
| `make run-sim` | backend 없이 로컬 시뮬레이션을 실행합니다. |
| `make dev` | backend + ai-server + frontend를 로컬에서 함께 띄웁니다. |
| `make up` | Docker Compose로 전체 스택을 띄웁니다. |
| `make ci-local` | 로컬 기준의 CI 검증 흐름을 실행합니다. |

## 4. 환경 변수 요약

`.env.example` 기준으로 자주 보는 항목만 먼저 정리하면 아래와 같습니다.

| 변수 | 기본값 | 의미 |
|---|---|---|
| `OPENAI_API_KEY` | 빈 값 | 실제 OpenAI 호출 시 필요합니다. |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | API base URL입니다. |
| `OPENAI_MODEL` | `gpt-5.2` | 기본 모델 이름입니다. |
| `CODEX_EXEC_MODE` | `disabled` | Codex 실행 활성화 여부입니다. |
| `CODEX_COMMAND_TEMPLATE` | `codex exec --json --cwd {workspace}` | Codex CLI 실행 템플릿입니다. |
| `AI_SERVER_URL` | `http://localhost:8000` | backend가 바라보는 AI 서버 주소입니다. |
| `BACKEND_URL` | `http://localhost:8080` | 예제 실행 시 사용하는 backend 주소입니다. |
| `VITE_BACKEND_URL` | `http://localhost:8080` | frontend가 바라보는 backend 주소입니다. |
| `VITE_AI_SERVER_URL` | `http://localhost:8000` | frontend가 바라보는 AI 서버 주소입니다. |
| `RAG_DOCS_DIR` | `docs` | RAG 문서 디렉터리 기본값입니다. |
| `AXBUILDER_WORKSPACE` | `.workspace` | workspace 루트 경로입니다. |
| `AXB_SECURITY_ENABLED` | `false` | 보안 기능 토글입니다. |
| `AXB_CORS_ALLOWED_ORIGINS` | `http://localhost:5173,...` | CORS 허용 origin 목록입니다. |

## 5. 포트와 health check

| 서비스 | 기본 포트 | health/check |
|---|---|---|
| Frontend | `5173` | 브라우저 접속 |
| AI Server | `8000` | `GET /health` |
| Backend | `8080` | `GET /api/v1/spec-runs/health`, `GET /actuator/health` |

서비스별 개별 실행은 [../guide/local-development.md](../guide/local-development.md)에서 더 자세히 정리했습니다.

## 6. CLI 흐름 예시

### Linux / macOS

```bash
python3 specyn.py validate --spec-dir specs/examples/todo-service
python3 specyn.py compile-prompts --spec-dir specs/examples/todo-service --output-dir .specyn/prompts/todo-service --workspace .workspace/todo-service
python3 specyn.py run --spec-dir specs/examples/todo-service --workspace .workspace/todo-service
```

### Windows (PowerShell)

```powershell
python specyn.py validate --spec-dir specs/examples/todo-service
python specyn.py compile-prompts `
  --spec-dir specs/examples/todo-service `
  --output-dir .specyn/prompts/todo-service `
  --workspace .workspace/todo-service
python specyn.py run `
  --spec-dir specs/examples/todo-service `
  --workspace .workspace/todo-service
```

## 7. GitHub Actions CI 구성

현재 workflow는 아래 세 축으로 동작합니다.

| Job | 검증 내용 |
|---|---|
| `backend` | Gradle test |
| `python` | spec bundle check, pytest, ruff format check |
| `frontend` | npm install, typecheck, build |

따라서 문서나 spec 템플릿을 바꿨더라도 결국 backend/python/frontend 세 축이 함께 어긋나지 않는지 확인해 보는 편이 좋습니다.

## 8. 운영 확장 포인트

- branch-per-run
- workspace isolation
- queue 기반 비동기 실행
- artifact 저장소 연계
- prompt snapshot / execution trace 보관
- dashboard / timeline / agent audit 기능 연계

## 9. 함께 보면 좋은 문서

- 빠른 시작: [quickstart.md](quickstart.md)
- 문제 해결: [troubleshooting.md](troubleshooting.md)
- 로컬 운영 상세: [../guide/local-development.md](../guide/local-development.md)
- 유지보수 체크리스트: [../guide/maintainer.md](../guide/maintainer.md)
