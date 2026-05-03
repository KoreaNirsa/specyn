# Tools

주요 CLI 구현은 `tools/specyn.py`, 로컬 산출물 생성은 `tools/local_sdd_runtime.py` 가 담당합니다.

## 핵심 동작

- `python specyn.py validate --spec-dir specs/001-sample-service`
- `python specyn.py compile-prompts --spec-dir specs/001-sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service`
- `python specyn.py run --spec-dir specs/001-sample-service --project-id sample-service --workspace .workspace/sample-service`

생성 결과는 `projects/sample-service/*` 아래로 저장됩니다.
