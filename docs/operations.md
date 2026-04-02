# 운영 가이드

## 권장 실행 순서

```text
setup
  -> auth-status
  -> doctor
  -> up -d
  -> sample-up -d
```

## 필수 로컬 도구

최초 실행 전 아래 도구를 설치합니다.

- Docker Desktop
- Python 3.11+
- Node.js 20+ 및 npm

확인:

```bash
python --version
node --version
npm --version
docker version
```

## 핵심 명령

| 명령 | 목적 |
|---|---|
| `python specyn.py setup` | `.env` 생성/갱신, 인증 방식 선택, 모델 선택, Docker agent 준비 확인 |
| `python specyn.py auth-status` | 인증 모드, Docker 준비 상태, 로컬 캐시 상태 확인 |
| `python specyn.py doctor` | 로컬 도구체인과 Docker 연동 준비 상태 점검 |
| `python specyn.py up -d` | dashboard frontend/backend/AI server 시작 |
| `python specyn.py down` | dashboard 스택 종료 |
| `python specyn.py sample-up -d` | sample-service 스택 시작 |
| `python specyn.py sample-down` | sample-service 스택 종료 |
| `python specyn.py validate ...` | spec bundle 검증 |
| `python specyn.py compile-prompts ...` | `.specyn/prompts/...` 아래 prompt 파일 생성 |
| `python specyn.py run ...` | 로컬 SDD 흐름 실행 |

## 인증 모드

### `chatgpt`

- 로컬 ChatGPT 연동 Codex 로그인 캐시를 사용합니다.
- 캐시는 `.specyn/codex` 아래에 저장됩니다.
- Docker agent 가 같은 로그인 상태를 재사용하려면 Docker Desktop 이 켜져 있어야 합니다.

### `openapi`

- `.env` 의 `OPENAI_API_KEY` 를 사용합니다.
- `.env` 는 민감 정보로 취급합니다.
- 커밋하거나 공유하지 않습니다.

## 로컬 전용 파일

다음 항목은 로컬 산출물이므로 커밋하지 않습니다.

- `.env`
- `.env.*`
- `.specyn/`
- `.workspace/`
- `node_modules/`
- 로컬 로그와 캐시

## 보안 메모

- `.env` 와 `.specyn/codex` 는 버전 관리에서 제외합니다.
- 외부로 로그를 공유하기 전 민감 정보 포함 여부를 확인합니다.
- `openapi` 모드에서 키 노출이 의심되면 즉시 교체합니다.

## 주요 포트

| 서비스 | 포트 | URL |
|---|---|---|
| Dashboard Frontend | `4173` | `http://localhost:4173` |
| Dashboard Backend | `8180` | `http://localhost:8180/api/v1/spec-runs/health` |
| Dashboard AI Server | `8100` | `http://localhost:8100/health` |
| sample-service Frontend | `5173` | `http://localhost:5173` |
| sample-service Backend | `8080` | `http://localhost:8080/api/v1/generated/sample-service/summary` |
| sample-service AI Server | `8000` | `http://localhost:8000/generated/sample-service/context` |
