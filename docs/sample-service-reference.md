# sample-service Reference

`sample-service` 는 Specyn의 실행 가능한 reference sample 입니다.

## Spec 위치

- `specs/001-sample-service/`

## 생성 위치

- `projects/sample-service/frontend`
- `projects/sample-service/backend`
- `projects/sample-service/ai-server`
- `projects/sample-service/docs`

## 실행 주소

- Frontend: `http://localhost:5173`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI context: `http://localhost:8000/generated/sample-service/context`

## 실행 순서

```bash
python specyn.py validate --spec-dir specs/001-sample-service
python specyn.py compile-prompts --spec-dir specs/001-sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/001-sample-service --project-id sample-service --workspace .workspace/sample-service
python scripts/specyn_tasks.py sample-dev
```
