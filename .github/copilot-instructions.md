# Specyn repository instructions

- Specyn is a spec-first SDD framework. Prefer changing spec, docs, tests, and generated outputs together instead of patching implementation only.
- Do not break the primary user path: `bootstrap -> doctor -> sample-flow -> dev`.
- The main runnable reference is `specs/projects/sample-service`. Keep quickstart, README, sample-service, and generated artifacts aligned.
- When changing agent flow or validator behavior, update the related docs and tests.
- When changing runtime behavior, verify `python specyn.py validate --spec-dir specs/projects/sample-service`, `python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service`, `python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service`, and `pytest -q`.
- For frontend changes, preserve the generated sample page under `frontend/src/generated/sample-service/` and keep `npm run build` working.
- For backend changes, keep generated sample endpoints and `gradle test` working.
- For AI server changes, keep the health endpoint and generated router loading working.
- Prefer friendly Korean documentation tone in README/docs/guide, while keeping important project terms discoverable in English where it helps.
