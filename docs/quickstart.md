# 🚀 Quick Start

이 문서는 **처음 저장소를 받은 사용자가 실제로 `specyn.py run` 까지 실행하고, 샘플 CRUD 웹사이트가 뜨는지 확인하는 최소 경로**를 안내합니다.

## 무엇을 확인하게 되나요?

이 Quick Start를 끝까지 따라가면 아래를 확인합니다.

1. `specs/projects/sample-service` spec bundle이 validate를 통과한다.
2. `compile-prompts` 로 agent prompt 산출물이 생성된다.
3. `specyn.py run` 으로 frontend/backend/ai-server/docs 산출물이 저장소에 생성된다.
4. `python scripts/specyn_tasks.py dev` 로 전체 개발 서버가 올라온다.
5. `http://localhost:5173/generated/sample-service` 에서 간단한 Task CRUD 웹사이트가 동작한다.

## 준비 사항

| 항목 | 필수 여부 | 권장 |
|---|---|---|
| Python | 필수 | 3.12+ |
| Node.js / npm | 필수 | 20+ |
| Java | 권장 | 21 |
| Gradle | 선택 | repo-local 또는 8.14+ |
| Docker | 선택 | Compose 실행 시 |
| OpenAI API Key | 선택 | Codex/외부 AI 연동 시 |

## 1) 기본 준비

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
python scripts/specyn_tasks.py bootstrap
python scripts/specyn_tasks.py doctor
```

### Linux / macOS

```bash
cp .env.example .env
python3 scripts/specyn_tasks.py bootstrap
python3 scripts/specyn_tasks.py doctor
```

`doctor` 에서는 Python / Node / npm / Java / Gradle / `.venv` 준비 상태를 확인합니다.

## 2) sample-service spec bundle 검증

```powershell
python specyn.py validate --spec-dir specs/projects/sample-service
```

정상이라면 `VALIDATION_OK` 가 출력됩니다.

## 3) prompt 파일 생성

### Windows (PowerShell)

```powershell
python specyn.py compile-prompts `
  --spec-dir specs/projects/sample-service `
  --output-dir .specyn/prompts/sample-service `
  --workspace .workspace/sample-service
```

### Linux / macOS

```bash
python3 specyn.py compile-prompts \
  --spec-dir specs/projects/sample-service \
  --output-dir .specyn/prompts/sample-service \
  --workspace .workspace/sample-service
```

생성 위치:

- `.specyn/prompts/sample-service/*.prompt.md`

## 4) `specyn.py run` 으로 실제 산출물 생성

### Windows (PowerShell)

```powershell
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service
```

### Linux / macOS

```bash
python3 specyn.py run \
  --spec-dir specs/projects/sample-service \
  --project-id sample-service \
  --workspace .workspace/sample-service
```

대표 산출물:

- `frontend/src/generated/sample-service/GeneratedProjectPage.tsx`
- `frontend/src/generated/sample-service/apiContract.ts`
- `backend/src/main/java/com/axbuilder/backend/generated/sample_service/GeneratedSampleServiceController.java`
- `ai-server/app/generated/sample_service/router.py`
- `docs/openapi/sample-service.yaml`
- `docs/generated/sample-service.md`
- `.workspace/sample-service/.specyn/runs/<run-id>/manifest.json`

## 5) 개발 서버 실행

```powershell
python scripts/specyn_tasks.py dev
```

정상이라면 Frontend / Backend / AI Server 주소가 준비 완료로 출력됩니다.

## 6) 브라우저에서 실제 결과 확인

먼저 이 주소를 엽니다.

- `http://localhost:5173/generated`
- `http://localhost:5173/generated/sample-service`

추가 확인 주소:

- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- Backend CRUD 목록: `http://localhost:8080/api/v1/tasks`
- AI Server context: `http://localhost:8000/generated/sample-service/context`

## 7) sample-service 에서 직접 해볼 것

1. 제목과 설명을 입력하고 **작업 생성** 버튼을 누릅니다.
2. 작업 카드에서 **상세 보기** 를 눌러 개별 JSON 응답을 확인합니다.
3. **상태 토글** 을 눌러 `PENDING` / `DONE` 전환을 확인합니다.
4. **삭제** 를 눌러 목록과 상세 상태가 갱신되는지 확인합니다.
5. 페이지 하단의 **Generated Summary** 와 **API Contract** 를 확인합니다.

## 8) 다음 문서

- `compile-prompts` 이후 흐름 설명: [playbook.md](playbook.md)
- `run` 옵션 상세: [cli-run-reference.md](cli-run-reference.md)
- 샘플 spec bundle 설명: [sample-service-reference.md](sample-service-reference.md)
- 로컬 개발 상세: [../guide/local-development.md](../guide/local-development.md)
