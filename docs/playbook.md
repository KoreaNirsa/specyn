# Playbook

## 권장 순서

### 기본 경로

1. `python specyn.py setup`
2. `python specyn.py auth-status`
3. `python specyn.py doctor`
4. `python specyn.py up -d`
5. `python specyn.py sample-up -d`

Docker Desktop 이 꺼져 있으면 1단계에서 `.env` 저장까지 먼저 끝난 뒤 agent 검증이 보류될 수 있습니다. 이 경우 Docker 시작 후 `setup` 또는 `doctor` 를 다시 실행합니다.

### 수동 spec 검증 경로

1. `python specyn.py validate --spec-dir specs/001-sample-service`
2. `python specyn.py compile-prompts --spec-dir specs/001-sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service`
3. `python specyn.py run --spec-dir specs/001-sample-service --project-id sample-service --workspace .workspace/sample-service`
4. `python scripts/specyn_tasks.py dev`
5. `python scripts/specyn_tasks.py sample-dev`

## 확인 포인트

- Dashboard: `http://localhost:4173`
- Dashboard Backend: `http://localhost:8180`
- Dashboard AI Server: `http://localhost:8100`
- sample-service Frontend: `http://localhost:5173`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI context: `http://localhost:8000/generated/sample-service/context`

## 운영 원칙

- 초기 설정은 `.env` 와 Docker agent 상태를 함께 고정하는 `python specyn.py setup` 을 기준으로 합니다.
- 대시보드 agent 실행은 Docker 컨테이너 내부에서 수행됩니다.
- 실제 프로젝트 산출물은 `projects/<project-id>/*` 아래에 생성됩니다.
- 관리자형 대시보드와 결과 프로젝트 런타임은 포트와 폴더를 공유하지 않습니다.
