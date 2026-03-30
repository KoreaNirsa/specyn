# 09. Troubleshooting

## 1. `make dev` 또는 `python scripts/specyn_tasks.py dev`가 실패한다

### 먼저 확인할 것
- `doctor` 출력
- `gradle.available`
- `npm.available`
- 포트 5173 / 8000 / 8080 점유 여부

### 대표 원인
- repo-local Gradle 다운로드 실패
- 시스템 Gradle 미설치
- Windows에서 npm 경로 해석 문제
- Frontend 의존성 미설치

### 권장 순서
1. `bootstrap`
2. `doctor`
3. `validate-spec`
4. `compile-prompts`
5. `run-sim`
6. 그 다음 `dev`

## 2. Windows에서 `npm` 또는 `gradle`을 못 찾는다

현재 task runner는 Windows의 `.cmd/.bat` 실행 파일을 처리하도록 보강되어 있다.
그래도 실패하면 아래를 확인한다.

- Node.js 설치 후 새 PowerShell 세션을 열었는지
- `npm.cmd`가 PATH에 있는지
- 사내 보안 정책으로 명령 실행이 차단되지 않는지

## 3. Gradle 다운로드가 막힌다

사내망/오프라인 환경에서는 repo-local Gradle 준비가 실패할 수 있다.
이 경우:

- 시스템 Gradle 8.14+ 설치
- 또는 Docker Compose 경로 사용

## 4. `validate`에서 spec 오류가 난다

가장 자주 발생하는 원인:
- YAML front matter 누락
- `목적/입력/출력/실행 규칙/Validation 기준/Prompt` 누락
- Prompt 내부 `Role/Instructions/Format` 누락
- `depends_on`이 실제 bundle과 맞지 않음
- `agent.md`의 `execution_flow`에 필수 agent 누락

## 5. `run-sim`은 되는데 실제 코드 생성은 안 된다

보통 아래 중 하나다.
- `OPENAI_API_KEY` 미설정
- `CODEX_EXEC_MODE=disabled`
- Codex CLI 미설치 또는 미인증

## 6. 무엇부터 봐야 할지 모르겠다

가장 안전한 순서는 아래다.

1. README
2. `docs/00-quickstart.md`
3. `docs/02-spec-driven-development.md`
4. `docs/03-agent-flow.md`
5. 예제 bundle(`specs/examples/todo-service`)
