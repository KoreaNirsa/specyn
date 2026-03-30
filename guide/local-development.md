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

## 5. backend 디렉터리에서 직접 실행하고 싶을 때

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

## 6. frontend를 직접 띄우고 싶을 때

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## 7. Docker Compose 경로

```bash
docker compose -f docker-compose.local.yml up --build
```

이 경로는 로컬 설치 편차를 줄이기에 좋습니다.

## 8. 운영 팁

| 상황 | 팁 |
|---|---|
| Gradle 다운로드가 막힙니다 | 시스템 Gradle 8.14+ 또는 Docker 경로를 먼저 고려해 보시면 좋습니다. |
| API Key 없이 흐름만 보고 싶습니다 | `run-sim` 경로부터 보시면 됩니다. |
| 포트 충돌이 납니다 | 5173 / 8000 / 8080 점유 여부를 먼저 보시면 됩니다. |
| prompt 산출물이 궁금합니다 | `.specyn/prompts`를 확인해 보시면 됩니다. |
