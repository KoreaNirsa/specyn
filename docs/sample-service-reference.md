# sample-service 참고

`sample-service` 는 Specyn의 reference sample 입니다. validator, prompt compiler, local runtime 흐름이 모두 이 bundle 기준으로 검증됩니다.

## spec 위치

- `specs/projects/sample-service/`

## 생성 위치

- `projects/sample-service/frontend`
- `projects/sample-service/backend`
- `projects/sample-service/ai-server`
- `projects/sample-service/docs`

## 실행 주소

- Frontend: `http://localhost:5173`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI context: `http://localhost:8000/generated/sample-service/context`

## 권장 실행 순서

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
python specyn.py sample-up -d
```

호스트 기반으로 직접 띄워 확인할 때만:

```bash
python scripts/specyn_tasks.py sample-dev
```
