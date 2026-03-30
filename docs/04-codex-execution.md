# 04. Codex Execution

Specyn은 두 가지 실행 경로를 제공합니다.

1. **로컬 CLI 런타임**: spec bundle을 deterministic scaffold로 변환해 저장소에 바로 생성
2. **Backend + AI Server + Codex**: prompt를 AI Server로 보내고 Codex CLI가 실제 patch/file 생성을 수행

이 문서는 두 번째 경로, 즉 **Codex 실행 환경**을 설명합니다.

---

## 1. 전체 흐름

```text
spec bundle
  -> specyn.py run --backend-url ...
  -> Spring Boot Backend (workflow 구성)
  -> FastAPI AI Server (prompt build)
  -> Codex CLI (실제 파일 생성/수정)
  -> workspace 반영
```

Backend는 agent 순서를 결정하고, AI Server는 prompt를 조합하며, Codex CLI는 `CODEX_COMMAND_TEMPLATE`에 따라 실제 작업 디렉터리에서 파일을 수정합니다.

---

## 2. 필수 환경 변수

### Linux / macOS

```bash
export CODEX_EXEC_MODE=cli
export CODEX_COMMAND_TEMPLATE='codex exec --json --cwd {workspace}'
```

### Windows (PowerShell)

```powershell
$env:CODEX_EXEC_MODE = "cli"
$env:CODEX_COMMAND_TEMPLATE = "codex exec --json --cwd {workspace}"
```

추가로 실제 모델 호출이 필요한 조직 환경이라면 OpenAI API Key 또는 사내 프록시 구성이 필요할 수 있습니다.

---

## 3. dev 서버 실행

### Linux / macOS

```bash
make dev
```

### Windows (PowerShell)

```powershell
python scripts/specyn_tasks.py dev
```

기본 포트는 아래와 같습니다.

- Frontend: `5173`
- AI Server: `8000`
- Backend: `8080`

---

## 4. Codex로 현재 저장소를 직접 수정하는 예시

이 방식은 결과를 바로 `frontend`, `backend`, `ai-server`에 반영하고 싶을 때 사용합니다.

### Linux / macOS

```bash
python3 specyn.py run \
  --backend-url http://localhost:8080 \
  --spec-dir specs/projects/sample-service \
  --project-id sample-service \
  --workspace .
```

### Windows (PowerShell)

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .
```

`--workspace .` 는 Codex가 **현재 저장소 루트**를 작업 디렉터리로 사용하게 만든다는 뜻입니다.

---

## 5. 안전한 분리 workspace에서 실행하는 예시

작업 결과를 먼저 별도 폴더에서 검토하고 싶다면 workspace를 분리합니다.

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service-codex
```

이 경우 Codex는 `.workspace/sample-service-codex` 아래를 수정합니다.

---

## 6. 로컬 CLI 런타임과의 차이

| 항목 | 로컬 CLI 런타임 | Codex 실행 환경 |
|---|---|---|
| 실행 명령 | `specyn.py run` | `specyn.py run --backend-url ...` |
| 코드 생성 방식 | 내장 deterministic generator | prompt + Codex CLI |
| 저장 위치 | 저장소의 고정 경로 | `--workspace` 경로 |
| 추천 용도 | scaffold 확인, 예제 데모, 문서/계약 초안 | 실제 patch 생성, 반복 수정, 사람 검토 |

---

## 7. 운영 팁

- 저장소를 직접 수정할 때는 `--workspace .` 를 사용합니다.
- 안전한 시도나 비교가 필요할 때는 `.workspace/<project>` 를 사용합니다.
- prompt snapshot은 workspace의 `.specyn/last_codex_prompt.md` 와 `.specyn/prompts/...` 에 남습니다.
- `agent.md`의 feedback loop가 많을수록 Codex 호출 횟수도 늘어납니다.
- destructive change가 가능한 프롬프트라면 branch-per-run, ephemeral workspace, human review gate를 함께 두는 편이 안전합니다.
