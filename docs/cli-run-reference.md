# CLI 실행 참고

## 기본 원칙

Specyn의 기본 CLI 진입점은 `python specyn.py` 입니다. 아래 명령은 모두 레포 루트에서 실행합니다.

## `setup`

```bash
python specyn.py setup
```

역할:

- `.env` 생성 또는 갱신
- `chatgpt` / `openapi` 인증 모드 선택
- ChatGPT 로그인 재사용 또는 재로그인
- `OPENAI_API_KEY` 입력 또는 갱신
- 실행 모델 선택
- Docker 사용 가능 시 agent 준비 상태 확인

## `auth-status`

```bash
python specyn.py auth-status
```

확인 항목:

- 현재 인증 모드
- API 키 존재 여부
- Docker 준비 상태 힌트
- 로컬 Codex 인증 캐시 힌트

## `doctor`

```bash
python specyn.py doctor
```

확인 항목:

- Python
- Node.js / npm
- Docker CLI 와 daemon
- 로컬 실행 준비 상태

## `up -d` / `down`

```bash
python specyn.py up -d
python specyn.py down
```

대시보드 스택을 시작하고 종료합니다.

## `sample-up -d` / `sample-down`

```bash
python specyn.py sample-up -d
python specyn.py sample-down
```

sample-service 런타임 스택을 시작하고 종료합니다.

## `validate`

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
```

spec bundle 필수 섹션, 구조, validator 규칙을 확인합니다.

## `compile-prompts`

```bash
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
```

agent 실행에 필요한 prompt 파일을 `.specyn/prompts/` 아래에 생성합니다.

## `run`

```bash
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
```

spec bundle 을 기준으로 agent 흐름을 실행하고 생성 결과를 `projects/sample-service` 와 `.workspace/sample-service` 아래에 기록합니다.

## 보조 호스트 실행 모드

아래 명령은 선택 사항입니다. Docker Compose 대신 로컬 프로세스를 직접 띄울 때 사용합니다.

```bash
python scripts/specyn_tasks.py dev
python scripts/specyn_tasks.py sample-dev
```

## 보안 메모

- `.env` 는 로컬 전용입니다.
- `.specyn/codex` 는 로컬 전용입니다.
- `.workspace/` 는 검토 전까지 로컬 산출물로 취급합니다.
- 커밋 전 `.gitignore` 와 생성 결과를 확인합니다.
