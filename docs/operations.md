# ⚙️ 운영 및 실행 가이드

이 문서는 Specyn 의 실행 모드, 자주 쓰는 명령, 환경 변수, 운영 포인트를 정리합니다.

## 1. 빠른 온보딩 명령

가장 빠른 로컬 온보딩은 아래 두 단계입니다.

```powershell
python scripts/specyn_tasks.py doctor
python scripts/specyn_tasks.py sample-flow
```

`sample-flow` 는 sample-service 기준으로 `validate -> compile-prompts -> run` 을 연속 실행합니다.

## 2. 실행 모드 비교

| 모드 | 대표 명령 | 목적 |
|---|---|---|
| 기본 검증 | `bootstrap`, `doctor`, `validate`, `compile-prompts` | 환경 준비와 spec/prompt 확인 |
| 빠른 샘플 검증 | `python scripts/specyn_tasks.py sample-flow` | sample-service 전체 흐름을 가장 짧게 재현 |
| 로컬 SDD 실행 | `specyn.py run --runtime local` | generated 코드와 문서를 저장소에 직접 생성 |
| 로컬 시뮬레이션 | `specyn.py run --runtime simulate` 또는 `run-sim` | 흐름 점검용 결과 확인 |
| 통합 개발 실행 | `python scripts/specyn_tasks.py dev` | Frontend + Backend + AI Server 확인 |
| Codex 실행 환경 | `specyn.py run --backend-url ...` | Backend/AI Server/Codex 연동 |
| Docker Compose | `docker compose -f docker-compose.local.yml up --build` | 환경 편차를 줄인 전체 실행 |

## 3. 가장 안전한 실행 순서

```text
bootstrap
  -> doctor
  -> sample-flow
  -> dev
```

개별 단계를 더 자세히 보고 싶다면 아래 수동 순서를 사용합니다.

```text
doctor
  -> validate
  -> compile-prompts
  -> run
  -> dev
```

## 4. 자주 쓰는 명령

| 명령 | 설명 |
|---|---|
| `python scripts/specyn_tasks.py bootstrap` | Python/Frontend 의존성과 작업 디렉터리 준비 |
| `python scripts/specyn_tasks.py doctor` | Python, Node, npm, Java, Gradle, Docker, `.venv` 상태 점검 |
| `python scripts/specyn_tasks.py sample-flow` | sample-service 기준 `validate -> compile-prompts -> run` 연속 실행 |
| `python specyn.py validate --spec-dir ...` | spec bundle 검증 |
| `python specyn.py compile-prompts --spec-dir ... --output-dir ... --workspace ...` | agent prompt 파일 생성 |
| `python specyn.py run --spec-dir ... --project-id ... --workspace ...` | 로컬 SDD 실행 |
| `python specyn.py run --backend-url http://localhost:8080 ...` | Codex 실행 환경 경유 |
| `python scripts/specyn_tasks.py dev` | Frontend/Backend/AI Server 통합 실행 |

## 5. sample-service 기준 추천 명령

### 빠른 경로

```powershell
python scripts/specyn_tasks.py sample-flow
python scripts/specyn_tasks.py dev
```

### 수동 경로

```powershell
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

## 6. 주요 환경 변수

| 변수 | 기본값 | 의미 |
|---|---|---|
| `OPENAI_API_KEY` | 빈 값 | 외부 OpenAI 호출 시 필요 |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | OpenAI compatible base URL |
| `OPENAI_MODEL` | `gpt-5.2` | 기본 모델 이름 |
| `CODEX_EXEC_MODE` | `disabled` | Codex 실행 활성화 여부 |
| `CODEX_COMMAND_TEMPLATE` | `codex exec --json --cwd {workspace}` | Codex CLI 실행 템플릿 |
| `AI_SERVER_URL` | `http://localhost:8000` | Backend 가 호출하는 AI Server 주소 |
| `BACKEND_URL` | `http://localhost:8080` | CLI/UI 에서 사용하는 Backend 주소 |
| `VITE_BACKEND_URL` | `http://localhost:8080` | Frontend 가 호출하는 Backend 주소 |
| `VITE_AI_SERVER_URL` | `http://localhost:8000` | Frontend 가 호출하는 AI Server 주소 |
| `AXB_CORS_ALLOWED_ORIGINS` | `http://localhost:5173,...` | 개발용 CORS 허용 origin |
| `AXB_SECURITY_ENABLED` | `false` | 로컬 보안 기능 토글 |
| `AXBUILDER_WORKSPACE` | `.workspace` | workspace 루트 |

## 7. 포트와 health check

| 서비스 | 포트 | 확인 주소 |
|---|---|---|
| Frontend | `5173` | `http://localhost:5173/` |
| AI Server | `8000` | `http://localhost:8000/health` |
| Backend | `8080` | `http://localhost:8080/api/v1/spec-runs/health` |
| Backend Actuator | `8080` | `http://localhost:8080/actuator/health` |

## 8. 운영 메모

- 처음 구조를 검증할 때는 Codex 보다 로컬 CLI 런타임이 더 안정적입니다.
- `sample-service` 는 실제 CRUD 확인용 reference sample 입니다.
- run 결과 추적은 `.workspace/<project>/.specyn/runs/<run-id>` 에 남습니다.
- generated 코드와 docs 가 어긋나면 spec bundle 을 source of truth 로 보고 다시 `validate -> compile-prompts -> run` 순서로 갱신합니다.

## 9. 관련 문서

- 빠른 시작: [quickstart.md](quickstart.md)
- `run` 옵션: [cli-run-reference.md](cli-run-reference.md)
- sample-service 참고: [sample-service-reference.md](sample-service-reference.md)
- 로컬 개발 상세: [../guide/local-development.md](../guide/local-development.md)
