# 메인테이너 체크리스트

이 문서는 Specyn 레포를 관리할 때 변경 영향 범위와 점검 포인트를 빠르게 확인하기 위한 가이드입니다.

## 변경 영향 매트릭스

| 변경한 위치 | 함께 확인할 항목 |
|---|---|
| `specs/templates/` | `specs/projects/sample-service/`, validator, 문서 |
| `agents/*.md` | prompt compiler, 실행 흐름 문서, sample bundle |
| `specyn.py` | README, quickstart, CLI reference |
| `scripts/specyn_tasks.py` | 로컬 개발 가이드, Makefile, host helper 설명 |
| `dashboard/backend/` | backend CI, API 문서, health check |
| `dashboard/ai-server/` | endpoint 문서, OpenAI/Codex/RAG 흐름 |
| `dashboard/frontend/` | typecheck/build, 화면 가이드, 스크린샷/문구 |
| `docs/`, `guide/` | README 링크, 예시 명령, 포트/경로 설명 |

## 최소 점검 흐름

1. `python specyn.py setup`
2. `python specyn.py doctor`
3. `python specyn.py validate --spec-dir specs/projects/sample-service`
4. `python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service`
5. `python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service`

로컬 호스트 기반 점검이 필요하면 추가로:

6. `python scripts/specyn_tasks.py dev`
7. `python scripts/specyn_tasks.py sample-dev`

## 문서 편집 원칙

- 기본 진입점은 항상 `python specyn.py` 로 안내합니다.
- `scripts/specyn_tasks.py` 는 선택형 보조 경로로만 설명합니다.
- sample-service 포트와 URL 은 README, `docs/`, `guide/` 전반에서 같이 맞춥니다.
- 깨진 한글이나 오래된 경로가 보이면 부분 수정보다 기준 문서 전체를 갱신하는 편이 안전합니다.

## CI 확인 항목

현재 PR 기준 핵심 검증은 다음 축입니다.

- Python spec/테스트 검증
- Backend build
- Frontend typecheck/build

문서 변경만 보이더라도 sample-service 명령, 경로, 포트, 링크가 drift 되지 않았는지 함께 확인합니다.
