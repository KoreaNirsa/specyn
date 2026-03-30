# 04. Codex Execution

Specyn 은 두 실행 경로를 제공합니다.

1. **로컬 CLI 런타임**: `specyn.py run` 이 deterministic generated 산출물을 저장소에 직접 생성
2. **Backend + AI Server + Codex**: Backend/AI Server 를 거쳐 Codex CLI 가 실제 patch/file 생성 수행

이 문서는 두 번째 경로를 설명합니다.

## 1. 전체 흐름

```text
spec bundle
  -> specyn.py run --backend-url ...
  -> Spring Boot Backend
  -> FastAPI AI Server
  -> Codex CLI
  -> workspace 반영
```

## 2. 언제 이 모드를 쓰나요?

다음 경우에 적합합니다.

- deterministic scaffold 를 넘어서 실제 Codex patch 를 생성하고 싶다.
- 현재 저장소 또는 별도 workspace 에 AI 기반 수정 결과를 반영하고 싶다.
- 사람 검토 전제의 반자동 workflow 를 실험하고 싶다.

처음 실행해 보는 경우에는 **먼저 로컬 CLI 런타임**으로 흐름을 확인하는 편이 좋습니다.

## 3. 준비 사항

- `.env` 생성
- `bootstrap`, `doctor` 완료
- Backend / AI Server / Frontend 실행
- Codex CLI 설치 및 인증
- 환경 변수 설정

### PowerShell 예시

```powershell
$env:CODEX_EXEC_MODE = "cli"
$env:CODEX_COMMAND_TEMPLATE = "codex exec --json --cwd {workspace}"
python scripts/specyn_tasks.py dev
```

## 4. 현재 저장소를 직접 수정하는 예시

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .
```

`--workspace .` 는 Codex 가 현재 저장소 루트를 직접 작업 디렉터리로 사용한다는 뜻입니다.

## 5. 격리 workspace 에서 실행하는 예시

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service-codex
```

이 경우 결과는 격리된 workspace 에 반영되므로 비교와 롤백이 쉽습니다.

## 6. 로컬 CLI 런타임과의 차이

| 항목 | 로컬 CLI 런타임 | Codex 실행 환경 |
|---|---|---|
| 실행 명령 | `specyn.py run` | `specyn.py run --backend-url ...` |
| 생성 방식 | deterministic generator | prompt + Codex CLI |
| 주요 목적 | 구조/문서/샘플 확인 | 실제 patch 생성 |
| 추천 시점 | 첫 실행, 데모, 학습 | 고급 실험, 반자동 코드 수정 |

## 7. 같이 보면 좋은 문서

- 실행 옵션: [cli-run-reference.md](cli-run-reference.md)
- 전체 적용 흐름: [playbook.md](playbook.md)
- 로컬 개발 상세: [../guide/local-development.md](../guide/local-development.md)
