# 🧪 로컬 개발 및 운영 가이드

이 문서는 서비스를 **통합으로 한 번에 띄우는 경우**와 **계층별로 나눠 띄우는 경우**를 모두 정리합니다.

## 1. 기본 포트 맵

| 서비스 | 기본 포트 | 비고 |
|---|---|---|
| Frontend | `5173` | Vite 개발 서버 |
| AI Server | `8000` | FastAPI |
| Backend | `8080` | Spring Boot |

## 2. health check 주소

| 서비스 | 주소 |
|---|---|
| AI Server | `GET http://localhost:8000/health` |
| Backend | `GET http://localhost:8080/api/v1/spec-runs/health` |
| Backend Actuator | `GET http://localhost:8080/actuator/health` |

## 3. 전체 로컬 네이티브 실행

### Linux / macOS

```bash
cp .env.example .env
make bootstrap
make doctor
make dev
```

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
python scripts/specyn_tasks.py bootstrap
python scripts/specyn_tasks.py doctor
python scripts/specyn_tasks.py dev
```

`dev`는 readiness check까지 수행하므로, AI Server / Backend / Frontend가 준비되면 각 주소를 출력합니다.

## 4. 서비스별 개별 실행

### AI Server만 실행

```bash
make ai-server
```

### Backend만 실행

```bash
make backend
```

### Frontend만 실행

```bash
make frontend
```

이 방식은 특정 계층만 집중해서 디버깅할 때 편합니다.

## 5. `specyn run` 이후 바로 확인할 생성 결과

로컬 CLI 런타임으로 아래 명령을 실행하면,

```powershell
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service
```

아래 산출물이 저장소에 직접 생성됩니다.

| 계층 | 생성 경로 |
|---|---|
| Frontend | `frontend/src/generated/<project>/GeneratedProjectPage.tsx` |
| Frontend contract | `frontend/src/generated/<project>/apiContract.ts` |
| Backend | `backend/src/main/java/com/axbuilder/backend/generated/<project>/...Controller.java` |
| AI Server | `ai-server/app/generated/<project>/router.py` |
| Docs | `docs/generated/<project>.md` |
| OpenAPI | `docs/openapi/<project>.yaml` |

샘플 기준으로는 다음 주소를 바로 열어 보면 됩니다.

| 확인 대상 | 주소 |
|---|---|
| generated page 목록 | `http://localhost:5173/generated` |
| generated project page | `http://localhost:5173/generated/sample-service` |
| generated backend summary | `http://localhost:8080/api/v1/generated/sample-service/summary` |
| generated ai-server context | `http://localhost:8000/generated/sample-service/context` |

## 6. backend 디렉터리에서 직접 실행하고 싶을 때

### Linux / macOS

```bash
cd backend
bash gradlew bootRun
```

### Windows (PowerShell)

```powershell
cd backend
.\gradlew.bat bootRun
```

## 7. frontend를 직접 띄우고 싶을 때

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## 8. Docker Compose 경로

```bash
docker compose -f docker-compose.local.yml up --build
```

이 경로는 로컬 설치 편차를 줄이기에 좋습니다.

## 9. Codex 모드에서 작업 경로를 정하는 법

`specyn.py run --backend-url ...` 는 `--workspace` 경로를 기준으로 Codex가 실제 파일을 수정합니다.

- 현재 저장소에 바로 반영: `--workspace .`
- 분리된 작업 디렉터리 사용: `--workspace .workspace/<project>-codex`

예시:

```powershell
python specyn.py run `
  --backend-url http://localhost:8080 `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .
```

## 10. 운영 팁

| 상황 | 팁 |
|---|---|
| Gradle 다운로드가 막힙니다 | 시스템 Gradle 8.14+ 또는 Docker 경로를 먼저 고려해 보시면 좋습니다. |
| API Key 없이 흐름만 보고 싶습니다 | `specyn.py run`의 로컬 CLI 런타임부터 보시면 됩니다. |
| 포트 충돌이 납니다 | 5173 / 8000 / 8080 점유 여부를 먼저 확인해 보시면 됩니다. |
| prompt 산출물이 궁금합니다 | `.specyn/prompts`를 확인해 보시면 됩니다. |
| run 결과 추적이 필요합니다 | `.workspace/<project>/.specyn/runs/<run-id>` 아래 manifest와 step report를 보시면 됩니다. |
