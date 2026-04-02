# Specs

- `specs/templates/` 는 새 프로젝트용 spec bundle 템플릿입니다.
- `specs/projects/sample-service/` 는 `validate`, `compile-prompts`, `run` 기준 reference sample 입니다.

## sample-service 기준 흐름

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
```

실제 생성 결과를 런타임으로 확인하려면:

```bash
python specyn.py sample-up -d
```

호스트 기반으로 직접 띄울 때만 아래 보조 명령을 사용합니다.

```bash
python scripts/specyn_tasks.py sample-dev
```
