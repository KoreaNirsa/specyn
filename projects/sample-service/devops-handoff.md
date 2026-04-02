STEP_LABEL: devops
AGENT: devops
PHASE: base
FEEDBACK_ROUND: 0
STATUS: done
CHANGED_FILES:
- /workspace/projects/sample-service/devops-handoff.md
- /workspace/projects/sample-service/docker-compose.local.yml
- /workspace/projects/sample-service/backend/Dockerfile
- /workspace/projects/sample-service/backend/.dockerignore
- /workspace/projects/sample-service/backend/build.gradle
- /workspace/projects/sample-service/backend/src/main/resources/application.yml
- /workspace/projects/sample-service/frontend/Dockerfile
- /workspace/projects/sample-service/frontend/docker/nginx.conf
- /workspace/projects/sample-service/frontend/.dockerignore
- /workspace/projects/sample-service/ai-server/Dockerfile
- /workspace/projects/sample-service/ai-server/requirements.txt
- /workspace/projects/sample-service/ai-server/app/main.py
- /workspace/projects/sample-service/ai-server/.dockerignore
- /workspace/projects/sample-service/.github/workflows/ci.yml
RESOLVED:
- 서비스별 컨테이너 이미지 빌드 경로(backend/frontend/ai-server)와 local compose 실행 단위를 고정.
- PostgreSQL 의존성과 health gate를 포함한 서비스 기동 순서 정의.
- backend liveness/readiness 엔드포인트를 actuator 기반으로 노출.
- CI baseline(backend test, frontend build, compose 검증) 추가.
UNRESOLVED:
- GitHub Actions 외 CI 벤더(GitLab/Jenkins) 템플릿은 미제공.
- `schema.sql` + `backend/db/migration` 이중 관리는 backend/dba 단계에서 단일화 필요.
BLOCKERS:
- none
NEXT_HANDOFF:
- Test Agent: compose 기준 e2e smoke(`create/list/detail/status/delete`) + `400/404/204` 검증 수행.
- Security Agent: DB 비밀번호 기본값 교체, 이미지 취약점 스캔, 런타임 권한 최소화 점검.
- Performance Agent: backend list pagination 전략과 DB connection pool 튜닝 포인트 검토.
- Docs Agent: 실행 명령(`docker compose -f docker-compose.local.yml up --build`)과 health URL 운영 문서 반영.

## 1) artifact/deploy unit summary
- Deploy units
  - `backend`: Spring Boot API + JDBC + Actuator (`/actuator/health/*`)
  - `frontend`: Nginx 정적 서빙 + `/api` reverse proxy
  - `ai-server`: FastAPI health service (`/health`)
  - `postgres`: 영속 데이터 저장소
- Rollback unit
  - 이미지 태그 단위 롤백(`backend`, `frontend`, `ai-server` 각각 독립 가능)
  - DB 스키마는 `V1__create_tasks.sql` 기준 non-destructive 시작

## 2) runtime/env contract
- Backend
  - `SERVER_PORT` (default `8080`)
  - `SPRING_DATASOURCE_URL`
  - `SPRING_DATASOURCE_USERNAME`
  - `SPRING_DATASOURCE_PASSWORD`
  - `SPRING_DATASOURCE_DRIVER_CLASS_NAME`
  - `APP_TASK_REPOSITORY` (`jdbc` | `memory`, default `jdbc`)
  - `AI_SERVER_URL`
- AI Server
  - `PORT` (default `8000`)
- Postgres
  - `POSTGRES_DB`
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`

Health/readiness/liveness 기준
- `ai-server`: `GET /health`가 200이면 healthy.
- `backend readiness`: `GET /actuator/health/readiness` 200.
- `backend liveness`: `GET /actuator/health/liveness` 200.
- `frontend`: `GET /healthz` 200.

## 3) CI/CD baseline
- CI jobs (`.github/workflows/ci.yml`)
  - `backend-test`: Java 21 + Gradle 8.14로 `gradle test`
  - `frontend-build`: Node 20 + `npm ci && npm run build`
  - `compose-validate`: `docker compose config`
- Pre-deploy quality gates
  - backend unit/integration tests pass
  - frontend build pass
  - compose validation pass
  - health endpoint 계약 유지

## 4) observability baseline
- Logs
  - backend/stdout: request error와 validation message 추적
  - frontend/nginx access log: route, status, upstream latency
  - ai-server/stdout: health check traffic
  - postgres log: connection/error 이벤트
- Metrics collection points
  - backend actuator health + JVM/process metrics(추후 prometheus exporter 확장 가능)
  - nginx request count/status ratio
  - postgres connection saturation / query latency
- Trace collection points
  - ingress(frontend nginx) -> backend -> DB hop에 공통 request id 헤더 도입 권장(후속 작업)

## 5) risks and follow-ups
- RISK: compose 기본 DB credential은 local 개발용이므로 staging/prod에서는 secret manager로 교체 필요.
- RISK: backend가 root가 아닌 유저로 실행되도록 이미지 hardening 추가 권장.
- RISK: `schema.sql`과 migration 파일 이중 관리로 drift 가능.
- FOLLOW-UP:
  1. Flyway/Liquibase 단일 migration 체계로 수렴.
  2. backend/frontend 이미지에 non-root 사용자 적용.
  3. CI에 컨테이너 빌드/스캔(job) 추가.
