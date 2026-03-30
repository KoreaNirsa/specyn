# 🧪 로컬 개발 가이드

이 문서는 **Specyn 을 로컬에서 실행하고 sample-service CRUD 결과까지 확인하는 절차**를 정리합니다.

## 1. 기본 포트

| 서비스 | 포트 |
|---|---|
| Frontend | `5173` |
| AI Server | `8000` |
| Backend | `8080` |

## 2. health check 주소

| 서비스 | 주소 |
|---|---|
| AI Server | `http://localhost:8000/health` |
| Backend health | `http://localhost:8080/api/v1/spec-runs/health` |
| Backend actuator | `http://localhost:8080/actuator/health` |

## 3. 가장 추천하는 로컬 실행 순서

```powershell
Copy-Item .env.example .env
python scripts/specyn_tasks.py bootstrap
python scripts/specyn_tasks.py doctor
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

## 4. `dev` 실행 후 확인할 주소

| 대상 | 주소 |
|---|---|
| Frontend 홈 | `http://localhost:5173/` |
| generated 목록 | `http://localhost:5173/generated` |
| sample-service CRUD 페이지 | `http://localhost:5173/generated/sample-service` |
| Backend summary | `http://localhost:8080/api/v1/generated/sample-service/summary` |
| Backend task 목록 | `http://localhost:8080/api/v1/tasks` |
| AI Server context | `http://localhost:8000/generated/sample-service/context` |

## 5. sample-service 에서 실제 확인 절차

1. generated 페이지를 연다.
2. 제목과 설명을 넣고 작업을 생성한다.
3. 목록 카드에서 상세 보기 버튼을 눌러 개별 JSON 응답을 확인한다.
4. 상태 토글 버튼을 눌러 `PENDING` / `DONE` 전환을 확인한다.
5. 삭제 버튼을 눌러 목록과 상세 상태가 같이 갱신되는지 확인한다.
6. 페이지 하단의 Generated Summary 와 API Contract 를 확인한다.

즉, 이 샘플은 **문서 참고용 spec 이면서 실제로 동작하는 아주 간단한 CRUD 웹사이트**를 목표로 합니다.

## 6. generated 파일 위치

| 영역 | 생성 경로 |
|---|---|
| Frontend page | `frontend/src/generated/<project>/GeneratedProjectPage.tsx` |
| Frontend contract | `frontend/src/generated/<project>/apiContract.ts` |
| Backend | `backend/src/main/java/com/axbuilder/backend/generated/<project>/...Controller.java` |
| AI Server | `ai-server/app/generated/<project>/router.py` |
| OpenAPI | `docs/openapi/<project>.yaml` |
| Generated docs | `docs/generated/<project>.md` |
| Run trace | `.workspace/<project>/.specyn/runs/<run-id>/...` |

## 7. 서비스별 개별 실행

### AI Server

```bash
python -m uvicorn app.main:app --app-dir ai-server --host 0.0.0.0 --port 8000 --reload
```

### Backend

```bash
cd backend
../.specyn/tools/gradle-8.14/bin/gradle bootRun
```

### Frontend

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

## 8. Codex 모드에서 workspace 선택

- 현재 저장소에 직접 반영: `--workspace .`
- 별도 작업 디렉터리 사용: `--workspace .workspace/<project>-codex`

예시:

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .
```

## 9. 운영 팁

- 첫 확인은 Codex 보다 로컬 CLI 런타임이 더 안정적입니다.
- generated 코드와 문서가 어긋나면 spec bundle 을 먼저 수정합니다.
- 포트 충돌이 있으면 5173 / 8000 / 8080 점유 여부를 먼저 봅니다.
- run 결과 추적은 `.workspace/<project>/.specyn/runs/<run-id>` 에서 확인합니다.
