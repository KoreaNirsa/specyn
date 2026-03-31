# Local Development

## 개발 모드 분리

- `python scripts/specyn_tasks.py dev` → dashboard/* 런타임
- `python scripts/specyn_tasks.py sample-dev` → projects/sample-service/* 런타임

## 핵심 명령

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
```

## 포트

- Dashboard: `http://localhost:4173`, `http://localhost:8180`, `http://localhost:8100`
- sample-service: `http://localhost:5173`, `http://localhost:8080/api/v1/generated/sample-service/summary`, `http://localhost:8000/generated/sample-service/context`
