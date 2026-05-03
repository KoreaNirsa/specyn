# Specs

- `.specify/memory/constitution.md` 는 Spec Kit 운영 원칙입니다.
- `specs/templates/` 는 새 spec bundle 시작 템플릿입니다.
- `specs/001-sample-service/` 는 실제로 validate -> compile-prompts -> run -> sample-dev 까지 검증하는 reference sample 입니다.
- `specs/002-todo-service/` 는 todo feature 예제 bundle 입니다.
- `specs/003-dashboard-design/` 는 현재 구현된 dashboard 기준 Design.md 스펙 bundle 입니다.
- `specs/004-grill-me/` 는 Grill Me 질문 기반 스펙 검증 절차 bundle 입니다.
- `specs/005-tdd-workflow/` 는 모든 향후 작업의 TDD gate 기준 bundle 입니다.

## Spec Kit Feature 구조

```text
specs/<number>-<feature-name>/
├── spec.md
├── api.md
├── tasks.md
├── review.md
├── plan.md
└── contracts/
```

## sample-service 실행

```bash
python specyn.py validate --spec-dir specs/001-sample-service
python specyn.py compile-prompts --spec-dir specs/001-sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/001-sample-service --project-id sample-service --workspace .workspace/sample-service
python scripts/specyn_tasks.py sample-dev
```
