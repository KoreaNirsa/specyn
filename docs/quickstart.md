# 빠른 시작

## 1. 사전 준비

다음 도구를 먼저 설치합니다.

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

## 2. 초기 설정

레포 루트에서 실행합니다.

```bash
python specyn.py setup
python specyn.py auth-status
python specyn.py doctor
```

`setup` 은 아래를 처리합니다.

- `.env` 생성 또는 갱신
- 인증 방식 선택
- ChatGPT 로그인 재사용 또는 재로그인
- `openapi` 모드용 API 키 입력
- 모델 선택
- Docker 사용 가능 시 agent 준비 상태 확인

## 3. 대시보드 시작

```bash
python specyn.py up -d
```

접속 주소:

- Frontend: `http://localhost:4173`
- Backend: `http://localhost:8180`
- AI Server: `http://localhost:8100`

## 4. agent 실행

대시보드의 `Workspace` 페이지로 이동해서 현재 spec bundle 을 실행합니다.

확인 포인트:

- `agent_message` 기반 실시간 진행 상황
- 단계별 상태와 요약
- 생성 산출물이 `projects/sample-service` 아래에 기록되는지 여부

## 5. sample-service 런타임 시작

생성된 결과를 실제 런타임으로 확인하려면:

```bash
python specyn.py sample-up -d
```

접속 주소:

- Frontend: `http://localhost:5173`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI context: `http://localhost:8000/generated/sample-service/context`

## 6. 수동 spec 실행

대시보드 없이도 spec 기준 흐름을 직접 실행할 수 있습니다.

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
```

## 7. 종료

```bash
python specyn.py down
python specyn.py sample-down
```

## 8. 주의 사항

- `.env`, `.specyn/codex`, `.workspace/` 는 로컬 전용으로 취급합니다.
- Docker Desktop 이 꺼져 있으면 `setup` 은 일부만 끝나고 실제 스택 기동은 되지 않습니다.
- 호스트 기반 보조 실행이 필요할 때만 `python scripts/specyn_tasks.py dev`, `python scripts/specyn_tasks.py sample-dev` 를 사용합니다.
