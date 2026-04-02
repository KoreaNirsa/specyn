## 변경 요약

- 

## 왜 필요한가

- 

## 확인한 항목

- [ ] `python specyn.py validate --spec-dir specs/projects/sample-service`
- [ ] `python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service`
- [ ] `python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service`
- [ ] 필요 시 `python scripts/specyn_tasks.py sample-dev`
- [ ] `pytest -q`
- [ ] 문서/가이드 링크 확인

## 영향 범위

- [ ] specs
- [ ] agents
- [ ] tools / runtime
- [ ] frontend
- [ ] backend
- [ ] ai-server
- [ ] docs / guide

## 추가 메모

- 
