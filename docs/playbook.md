# 플레이북

## 권장 실행 순서

### 기본 경로

1. `python specyn.py setup`
2. `python specyn.py auth-status`
3. `python specyn.py doctor`
4. `python specyn.py up -d`
5. 대시보드 `Workspace` 페이지에서 agent 실행
6. 필요 시 `python specyn.py sample-up -d`

Docker Desktop 이 꺼져 있으면 `.env` 갱신까지만 끝나고 agent 검증이나 스택 기동은 보류될 수 있습니다. 이 경우 Docker 를 먼저 켠 뒤 `doctor` 또는 `setup` 을 다시 실행합니다.

### 수동 spec 경로

1. `python specyn.py validate --spec-dir specs/projects/sample-service`
2. `python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service`
3. `python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service`
4. 필요 시 `python scripts/specyn_tasks.py dev`
5. 필요 시 `python scripts/specyn_tasks.py sample-dev`

## 확인할 주소

- Dashboard Frontend: `http://localhost:4173`
- Dashboard Backend: `http://localhost:8180`
- Dashboard AI Server: `http://localhost:8100`
- sample-service Frontend: `http://localhost:5173`
- sample-service Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- sample-service AI context: `http://localhost:8000/generated/sample-service/context`

## 운영 메모

- 기본 진입점은 `python specyn.py ...` 입니다.
- `scripts/specyn_tasks.py` 는 Docker Compose 대신 호스트 프로세스를 직접 띄우는 보조 도구입니다.
- 실제 생성 산출물은 `projects/<project-id>/` 와 `.workspace/<project-id>/` 아래에 기록됩니다.
- 문서와 README 를 업데이트할 때는 sample-service 경로, 포트, 실행 명령을 함께 맞춰야 합니다.
