# Playbook

## 권장 순서

1. `python specyn.py validate --spec-dir specs/projects/sample-service`
2. `python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service`
3. `python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service`
4. `python scripts/specyn_tasks.py dev`
5. `python scripts/specyn_tasks.py sample-dev`

## 확인 포인트

- Dashboard: `http://localhost:4173`
- sample-service Frontend: `http://localhost:5173`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI context: `http://localhost:8000/generated/sample-service/context`

## 운영 원칙

- 대시보드 런타임은 `dashboard/*` 에서만 동작합니다.
- 실제 프로젝트 산출물은 `projects/<project-id>/*` 아래에 생성됩니다.
- 관리자형 대시보드와 결과 프로젝트 런타임은 포트와 폴더를 공유하지 않습니다.
