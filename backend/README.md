# backend

Spring Boot 기반 Specyn 오케스트레이터다.

## 역할
- spec bundle 수신
- 필수 spec 검증
- `agent.md` 기반 실행 순서 해석
- FastAPI AI Server 호출
- 단계별 결과 집계

## 실행
### 루트에서 실행

#### Linux / macOS
```bash
make bootstrap
make backend
```

#### Windows (PowerShell)
```powershell
python scripts/specyn_tasks.py bootstrap
python scripts/specyn_tasks.py backend
```

`bootstrap`은 repo-local Gradle 8.14 준비를 함께 시도한다.

### backend 디렉터리에서 직접 실행

#### Linux / macOS
```bash
cd backend
bash gradlew bootRun
```

#### Windows (PowerShell)
```powershell
cd backend
.\gradlew.bat bootRun
```

## 주요 엔드포인트
- `POST /api/v1/spec-runs`
- `GET /api/v1/spec-runs/health`
- `GET /actuator/health`

## 설계 포인트
- 실행 순서는 정적 하드코딩보다 `agent.md`의 `execution_flow`를 우선한다.
- `feedback_loops`와 `max_feedback_rounds`가 있으면 bounded feedback round를 실행 계획에 포함한다.
- `ragEnabled=true`이면 지원되는 경우 `Planner` 다음에 `RAG`를 삽입한다.
- 결과는 최종적으로 agent step 목록으로 집계된다.

## 생성 대상 Spring Boot 구조 규약

Specyn이 생성하는 Spring Boot 서비스는 `global / common / domain` 구조를 권장한다.
현재 backend 런타임 자체는 프레임워크 호환성을 위해 기존 구조를 유지할 수 있지만, 사용자 프로젝트 산출물은 `docs/10-structure-conventions.md` 규약을 따르는 편이 안정적이다.
