# 로컬 개발

## 사전 준비

- Docker Desktop
- Python 3.11+
- Node.js 20+ 및 npm

권장 확인:

```bash
python --version
node --version
npm --version
docker version
```

## 표준 로컬 흐름

```bash
python specyn.py setup
python specyn.py auth-status
python specyn.py doctor
python specyn.py up -d
python specyn.py sample-up -d
```

Docker Desktop 이 꺼져 있으면 `setup` 은 `.env` 갱신까지만 끝날 수 있고, Docker 기반 검증이나 스택 기동은 완료되지 않습니다.

## 대시보드 스택

- Frontend: `http://localhost:4173`
- Backend: `http://localhost:8180`
- AI Server: `http://localhost:8100`

## sample-service 스택

- Frontend: `http://localhost:5173`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI context: `http://localhost:8000/generated/sample-service/context`

## 수동 spec 흐름

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
```

## 선택형 호스트 기반 실행

Docker Compose 대신 로컬 프로세스를 직접 띄우려면 아래 헬퍼를 사용합니다.

```bash
python scripts/specyn_tasks.py dev
python scripts/specyn_tasks.py sample-dev
```

이 모드는 보조 경로이며, 기본 사용법은 `python specyn.py up -d`, `python specyn.py sample-up -d` 입니다.

## 위생 수칙

- `.env` 는 커밋하지 않습니다.
- `.specyn/codex` 는 로컬 전용으로 유지합니다.
- `.workspace/` 는 로컬 산출물로 취급합니다.
- 생성 코드는 공유 브랜치에 올리기 전에 검토합니다.
- 로그를 외부에 붙여 넣기 전 민감 정보 포함 여부를 확인합니다.
