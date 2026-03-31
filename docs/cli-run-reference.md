# CLI Run Reference

## validate

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
```

## compile-prompts

```bash
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
```

## run

```bash
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
```

`run` 결과는 루트 `frontend/backend/ai-server`가 아니라 `projects/sample-service/frontend`, `projects/sample-service/backend`, `projects/sample-service/ai-server`, `projects/sample-service/docs` 로 기록됩니다.

## 로컬 실행

- `python scripts/specyn_tasks.py dev` → dashboard 실행
- `python scripts/specyn_tasks.py sample-dev` → sample-service 실행

### 확인 URL

- `http://localhost:4173`
- `http://localhost:5173`
- `http://localhost:8080/api/v1/generated/sample-service/summary`
- `http://localhost:8000/generated/sample-service/context`
