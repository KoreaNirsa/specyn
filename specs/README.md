# Specs

- `specs/templates/` 는 새 spec bundle 시작 템플릿입니다.
- `specs/projects/sample-service/` 는 실제로 validate → compile-prompts → run → sample-dev 까지 검증하는 reference sample 입니다.

## sample-service 실행

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
python scripts/specyn_tasks.py sample-dev
```
