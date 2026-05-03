# 04. Codex Execution

Specyn의 Codex 실행 경로는 **`.env` 기반 인증 + Docker agent** 를 기본으로 사용합니다.

## 1. 전체 흐름

```text
spec bundle
  -> python specyn.py setup
  -> .env / auth cache(.specyn/codex) 확정
  -> python specyn.py up -d
  -> dashboard-ai-server(Docker)
  -> Codex CLI(Docker agent 내부)
  -> workspace 반영
```

핵심 포인트는 **Codex 실행이 호스트가 아니라 Docker agent 컨테이너 안에서 수행된다**는 점입니다.

## 2. 왜 Docker agent를 쓰나요?

- 호스트에 Codex CLI를 직접 설치하지 않아도 됩니다.
- 로그인 캐시와 실행 모델을 `.env` + `CODEX_HOME` 기준으로 일관되게 관리할 수 있습니다.
- agent 실행 환경을 고정해서 호스트 편차 영향을 줄일 수 있습니다.

## 3. 인증 방식

### ChatGPT 계정

```bash
python specyn.py setup
```

- `SPECYN_AUTH_MODE=chatgpt`
- Docker daemon 이 준비된 상태라면 기존 로그인 캐시 유지 또는 재로그인 선택 가능
- 로그인 캐시는 `.specyn/codex` 아래에 저장

### OpenAI API Key

```bash
python specyn.py setup --auth-mode openapi
```

- `SPECYN_AUTH_MODE=openapi`
- API Key가 없으면 입력
- API Key가 있으면 유지 / 수정 / 제거 가능
- Docker daemon 이 준비되어 있으면 Docker agent와 AI Server가 같은 API Key 설정을 공유
- Docker daemon 이 준비되지 않았으면 `.env` 에 먼저 저장되고 컨테이너 내부 적용은 보류

## 4. 모델 선택

`setup` 실행 중 모델을 선택하면 아래 두 값이 함께 맞춰집니다.

```dotenv
OPENAI_MODEL=gpt-5.4
CODEX_MODEL=gpt-5.4
```

Codex 실행 명령은 `.env` 의 `CODEX_COMMAND_TEMPLATE` 를 사용합니다.

```dotenv
CODEX_COMMAND_TEMPLATE=codex exec --json --model {model} --cwd {workspace}
```

## 5. 실행 예시

### 대시보드 전체 실행

```bash
python specyn.py up -d
```

### sample-service 전체 실행

```bash
python specyn.py sample-up -d
```

### 수동 run 경로

```bash
python specyn.py run \
  --backend-url http://localhost:8080 \
  --spec-dir specs/001-sample-service \
  --project-id sample-service \
  --workspace .workspace/sample-service
```

## 6. 상태 확인

```bash
python specyn.py auth-status
python specyn.py doctor
```

- 인증 모드
- API Key 설정 여부
- Docker CLI / daemon 준비 여부
- repo-local 로그인 캐시 상태
- Docker agent 내부 Codex 설치 여부
- 현재 모델 설정

## 7. Docker Desktop 이 꺼져 있을 때

Windows 에서 아래 오류가 보이면 Docker daemon 연결 문제입니다.

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

이 경우 권장 순서는 아래입니다.

```bash
python specyn.py setup
# .env 저장 및 설정 고정

# Docker Desktop 시작 후
python specyn.py setup
python specyn.py doctor
python specyn.py up -d
```

## 8. 같이 보면 좋은 문서

- 빠른 시작: [quickstart.md](quickstart.md)
- 실행 옵션: [cli-run-reference.md](cli-run-reference.md)
- 운영 가이드: [operations.md](operations.md)
- 로컬 개발 상세: [../guide/local-development.md](../guide/local-development.md)
