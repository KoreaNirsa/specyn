# `specyn.py run` 명령 및 옵션 설명

이 문서는 `specyn.py run` 의 의미, 옵션, 실행 모드, 예시를 설명합니다.

## 1. 명령 개요

```text
python specyn.py run --spec-dir <SPEC_DIR> [--project-id <PROJECT_ID>] [--workspace <WORKSPACE>] [--backend-url <BACKEND_URL>] [--rag-enabled] [--runtime local|simulate]
```

`run` 은 두 방식으로 동작합니다.

1. **로컬 CLI 런타임**: `--backend-url` 없이 실행
2. **Backend/Codex 실행 환경**: `--backend-url` 을 주고 실행

## 2. 옵션 설명

### `--spec-dir`

- 의미: spec bundle 디렉터리 경로
- 필수 여부: **필수**
- 예시: `specs/projects/sample-service`

### `--project-id`

- 의미: 생성 프로젝트 식별자
- 기본값: spec dir 이름에서 유도되거나 내부 기본값 사용
- 권장: **항상 명시**
- 예시: `sample-service`

생성 파일 경로, 클래스명, generated route 이름 등에 반영됩니다.

### `--workspace`

- 의미: run trace, manifest, prompt 등 작업 산출물 기준 디렉터리
- 예시: `.workspace/sample-service`
- 권장: 프로젝트별로 분리된 workspace 사용

로컬 CLI 런타임에서는 주로 `.workspace/<project>` 를 권장합니다.
Codex 모드에서는 `.` 또는 별도 격리 workspace 를 선택할 수 있습니다.

### `--backend-url`

- 의미: Spring Boot Backend API URL
- 사용 시점: **Codex 실행 환경**에서 사용
- 예시: `http://localhost:8080`

이 옵션이 있으면 `run` 은 로컬 deterministic generator 대신 Backend 를 경유한 실행 경로를 사용합니다.

### `--rag-enabled`

- 의미: RAG 관련 흐름을 execution plan 에 반영
- 기본값: 비활성
- 사용 예시: 내부 문서 검색이나 보조 context 가 필요한 경우

### `--runtime {local,simulate}`

- 의미: `--backend-url` 없이 실행할 때의 로컬 런타임 모드
- 기본값: `local`

값 설명:

- `local`: 실제 generated 파일 생성
- `simulate`: 시뮬레이션 결과만 확인

## 3. 가장 자주 쓰는 실행 패턴

### 패턴 A. sample-service 를 로컬 CLI 런타임으로 실행

```powershell
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service
```

용도:

- 저장소 구조 검증
- generated 코드/문서 확인
- 샘플 CRUD 데모 확인

### 패턴 B. 현재 저장소에 Codex 결과를 직접 반영

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .
```

용도:

- Codex CLI 로 현재 저장소를 직접 수정
- patch/file 생성 실험

### 패턴 C. 별도 workspace 에 Codex 결과를 반영

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service-codex
```

용도:

- 안전하게 비교/검토
- 실패 복구가 쉬운 격리 경로 사용

### 패턴 D. simulate 로 흐름만 점검

```powershell
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service `
  --runtime simulate
```

용도:

- 실제 파일 생성 전 흐름 확인

## 4. `run` 이 생성하는 것

로컬 CLI 런타임 기준 대표 산출물:

- `frontend/src/generated/<project>/GeneratedProjectPage.tsx`
- `frontend/src/generated/<project>/apiContract.ts`
- `backend/src/main/java/com/axbuilder/backend/generated/<project>/...Controller.java`
- `ai-server/app/generated/<project>/router.py`
- `docs/openapi/<project>.yaml`
- `docs/generated/<project>.md`
- `.workspace/<project>/.specyn/runs/<run-id>/manifest.json`
- `.workspace/<project>/.specyn/runs/<run-id>/steps/*.md`

## 5. 실행 후 바로 확인할 주소

sample-service 기준:

- Frontend: `http://localhost:5173/generated/sample-service`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- Backend CRUD 목록: `http://localhost:8080/api/v1/tasks`
- AI Server context: `http://localhost:8000/generated/sample-service/context`

## 6. 흔한 실수

- `--spec-dir` 를 `specs/examples/todo-service` 로 두고 sample-service 결과를 기대함
- `--workspace .` 를 로컬 런타임에서도 무조건 사용해 작업 결과를 섞어 버림
- `compile-prompts` 없이 run 만 실행하고 prompt 산출물 위치를 기대함
- Codex 모드인데 `--backend-url` 을 빼먹음
- Codex 모드인데 `CODEX_EXEC_MODE` 와 `CODEX_COMMAND_TEMPLATE` 를 설정하지 않음

## 7. 추천 조합

가장 안전한 기본 조합:

```powershell
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts `
  --spec-dir specs/projects/sample-service `
  --output-dir .specyn/prompts/sample-service `
  --workspace .workspace/sample-service
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service
python scripts/specyn_tasks.py dev
```
