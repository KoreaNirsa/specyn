# 🛠 문제 해결 가이드

실행이 막혔을 때는 먼저 **가장 단순한 검증 경로로 내려와 상태를 확인**하는 편이 빠릅니다.

## 권장 복구 순서

```text
bootstrap
  -> doctor
  -> validate
  -> compile-prompts
  -> run
  -> dev
```

## 자주 발생하는 문제

| 증상 | 먼저 볼 것 | 대표 원인 |
|---|---|---|
| `bootstrap` 실패 | `frontend/package-lock.json`, npm registry, 네트워크 | 사내 registry 고정, npm 설치 실패 |
| `doctor` 에서 Gradle 오류 | repo-local Gradle 경로, Windows 실행 파일 | `gradle`/`gradle.bat` 선택 문제 |
| `dev` 에서 Backend compile 실패 | `backend/build.gradle.kts`, generated controller | Spring Boot 의존성/BOM 문제, Java API 불일치 |
| `run` 은 성공했는데 화면이 이상함 | generated frontend page, CSS, Backend API | generated page/class 스타일 누락, contract drift |
| 브라우저에서 API 호출 실패 | CORS, Backend/AI Server 포트 | `AXB_CORS_ALLOWED_ORIGINS`, 서비스 미기동 |
| Codex 모드가 실행되지 않음 | `CODEX_EXEC_MODE`, `CODEX_COMMAND_TEMPLATE` | Codex CLI 미설치, 인증 누락 |

## 1. `doctor` 부터 다시 확인

```powershell
python scripts/specyn_tasks.py doctor
```

특히 아래를 확인합니다.

- Python
- Node / npm
- Java
- Gradle
- `.venv`

## 2. spec bundle 자체가 맞는지 확인

```powershell
python specyn.py validate --spec-dir specs/projects/sample-service
```

자주 나오는 원인:

- YAML front matter 누락
- `목적 / 입력 / 출력 / 실행 규칙 / Validation 기준 / Prompt` 누락
- `agent.md` 의 execution flow / feedback loop 불일치
- `api.md` 의 endpoint 표 또는 request/response 예시 부족

## 3. `compile-prompts` 는 되는데 `run` 이 기대대로 안 된다

로컬 CLI 런타임 기준에서는 `specyn.py run` 이 **실제 generated 파일을 저장소에 직접 생성**합니다. 따라서 먼저 아래를 확인합니다.

- `frontend/src/generated/<project>`
- `backend/src/main/java/.../generated/...`
- `ai-server/app/generated/<project>`
- `docs/generated/<project>.md`
- `docs/openapi/<project>.yaml`
- `.workspace/<project>/.specyn/runs/<run-id>/manifest.json`

즉, **로컬 런타임에서는 OpenAI API Key 나 Codex CLI 없이도 generated 산출물이 생겨야 정상**입니다.

## 4. `dev` 는 떴는데 브라우저에서 확인이 어렵다

sample-service 기준 확인 순서:

1. `http://localhost:5173/generated`
2. `http://localhost:5173/generated/sample-service`
3. `http://localhost:8080/api/v1/generated/sample-service/summary`
4. `http://localhost:8080/api/v1/tasks`
5. `http://localhost:8000/generated/sample-service/context`

샘플 페이지에서 아래가 모두 동작해야 합니다.

- 생성
- 목록 조회
- 상세 조회
- 상태 토글
- 삭제

## 5. `dev` 중 특정 서비스만 실패한다

| 서비스 | 먼저 확인할 것 |
|---|---|
| Frontend | `npm`, `node_modules`, `VITE_BACKEND_URL`, `VITE_AI_SERVER_URL` |
| Backend | Java 21, Gradle, `backend/build.gradle.kts`, generated controller |
| AI Server | `.venv`, FastAPI import, Python 버전, CORS |

## 6. Codex 모드에서만 실패한다

Codex 모드는 로컬 런타임과 별개로 아래가 추가로 필요합니다.

- `CODEX_EXEC_MODE=cli`
- `CODEX_COMMAND_TEMPLATE` 설정
- Codex CLI 설치 및 인증
- Backend / AI Server 실행

즉, 로컬 CLI 런타임이 정상이라고 해서 Codex 모드까지 자동으로 준비되는 것은 아닙니다.

## 7. 그래도 복구가 어렵다면

다시 가장 짧은 경로로 돌아가 아래 순서를 재실행합니다.

```powershell
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

관련 문서:

- [quickstart.md](quickstart.md)
- [playbook.md](playbook.md)
- [cli-run-reference.md](cli-run-reference.md)
- [../guide/local-development.md](../guide/local-development.md)
