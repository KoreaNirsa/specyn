# 🛠 문제 해결 가이드

실행이 막혔을 때는 문제를 바로 정면 돌파하기보다, **가장 단순한 검증 경로로 다시 내려와서 상태를 확인하는 것**이 훨씬 빠를 때가 많습니다.

## 먼저 다시 확인해 보시면 좋은 순서

```text
bootstrap
  -> doctor
  -> validate-spec
  -> compile-prompts
  -> run-sim
  -> dev 또는 docker compose
```

## 자주 발생하는 문제 요약

| 증상 | 먼저 볼 것 | 대표 원인 |
|---|---|---|
| `make dev`가 실패합니다 | `doctor`, `gradle.available` | repo-local Gradle 다운로드 실패, 시스템 Gradle 미설치 |
| Windows에서 `npm`을 못 찾습니다 | PATH, 새 PowerShell 세션 | Node.js 설치 직후 셸 재시작 누락 |
| `validate`에서 spec 오류가 납니다 | spec 파일 구조 | YAML front matter나 필수 섹션 누락 |
| `run-sim`은 되는데 실제 생성이 안 됩니다 | `.env`, Codex 설정 | `OPENAI_API_KEY` 미설정, `CODEX_EXEC_MODE=disabled` |
| frontend가 backend를 못 찾습니다 | `VITE_BACKEND_URL`, 포트 | 5173/8080 포트 충돌 또는 URL 오설정 |

## 1. `make dev` 또는 `python scripts/specyn_tasks.py dev`가 실패합니다

### 먼저 확인할 것

- `make doctor` 또는 `python scripts/specyn_tasks.py doctor`
- `gradle.available`
- `npm.available`
- 포트 `5173`, `8000`, `8080` 점유 여부

### 권장 대응 순서

1. `bootstrap`
2. `doctor`
3. `validate-spec`
4. `compile-prompts`
5. `run-sim`
6. 그다음 `dev`

## 2. Windows에서 `npm` 또는 `gradle`을 찾지 못합니다

아래를 차례대로 확인해 보시면 좋습니다.

- Node.js 설치 후 **새 PowerShell 세션**을 열었는지
- `npm.cmd`가 PATH에 잡혀 있는지
- 사내 보안 정책이 `.cmd/.bat` 실행을 막고 있지 않은지
- 시스템 Gradle 또는 repo-local Gradle 준비가 가능한지

## 3. Gradle 다운로드가 막힙니다

사내망이나 오프라인 환경에서는 repo-local Gradle 준비가 실패할 수 있습니다.

이럴 때는 아래 순서가 현실적입니다.

1. 시스템 Gradle 8.14+ 설치
2. 또는 Docker Compose 경로 사용
3. 그래도 어렵다면 기본 검증 모드(`validate-spec`, `compile-prompts`, `run-sim`)로 먼저 확인

## 4. `validate`에서 spec 오류가 납니다

가장 자주 나오는 원인은 아래와 같습니다.

- YAML front matter 누락
- `목적/입력/출력/실행 규칙/Validation 기준/Prompt` 누락
- Prompt 내부 `Role/Instructions/Format` 누락
- `depends_on`이 실제 bundle 구조와 맞지 않음
- `agent.md`의 `execution_flow`에 필수 Agent 누락

이럴 때는 [sdd-principles.md](sdd-principles.md)를 함께 보면서 비교하시면 빠릅니다.

## 5. `run-sim`은 되는데 실제 코드 생성은 안 됩니다

보통 아래 중 하나입니다.

- `OPENAI_API_KEY`가 비어 있습니다.
- `CODEX_EXEC_MODE=disabled` 상태입니다.
- Codex CLI가 설치되지 않았거나 인증되지 않았습니다.

즉, **시뮬레이션 성공은 곧바로 실제 생성 준비 완료를 뜻하지는 않습니다.**

## 6. 어디서부터 봐야 할지 모르겠습니다

가장 안전한 순서는 아래입니다.

1. `README.md`
2. [quickstart.md](quickstart.md)
3. [sdd-principles.md](sdd-principles.md)
4. [agent-catalog.md](agent-catalog.md)
5. `specs/examples/todo-service`

## 7. 그래도 막힐 때 체크리스트

| 체크 항목 | 확인 여부 |
|---|---|
| `.env`가 생성되어 있는가 | ☐ |
| `.venv`가 정상 생성되었는가 | ☐ |
| frontend 의존성이 설치되었는가 | ☐ |
| `doctor` 결과를 확인했는가 | ☐ |
| 예제 spec bundle이 validate를 통과하는가 | ☐ |
| `run-sim`은 통과하는가 | ☐ |

추가로 서비스별 상세 점검이 필요하시면 [../guide/local-development.md](../guide/local-development.md)을 함께 보시는 편이 좋습니다.
