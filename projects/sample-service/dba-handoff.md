STEP_LABEL: dba
AGENT: dba
PHASE: feedback
FEEDBACK_ROUND: 1
STATUS: done
CHANGED_FILES:
- /workspace/projects/sample-service/dba-handoff.md
- /workspace/projects/sample-service/backend/db/migration/V1__create_tasks.sql
RESOLVED:
- Backend가 `domain.task.infrastructure.JdbcTaskRepository`를 도입해 영속 저장 경로를 실제로 사용 가능하게 됨.
- Backend runtime 스키마(`schema.sql`)와 DBA migration의 타입/제약 표현을 정렬해 drift를 축소.
- 저장소 fallback 전략이 설정화됨(`app.task.repository=jdbc|memory`).
UNRESOLVED:
- `schema.sql`(runtime init)과 `backend/db/migration`(DBA 산출물)이 이중 소스로 남아 있음.
- Flyway/Liquibase 같은 migration 실행 체계가 아직 연결되지 않음.
- 운영 DB(PostgreSQL) compose wiring 및 권한 분리(DDL/DML 사용자)가 미구현.
BLOCKERS:
- none
NEXT_HANDOFF:
- DevOps Agent: `docker-compose.local.yml`에 PostgreSQL 서비스와 `SPRING_DATASOURCE_*` 연결 추가.
- Backend Agent: migration 단일 소스화(`schema.sql` 제거 + Flyway 도입 또는 반대 방향 결정) 수행.
- Test Agent: `APP_TASK_REPOSITORY=jdbc` 기준 CRUD/404/400/204 회귀와 재시작 후 데이터 유지 검증.
- Performance Agent: 현재 list full-scan 정렬 구조에 pagination(`limit/offset` 또는 keyset) 도입 시점 평가.
- Security Agent: DB 최소권한 계정, 비밀값 주입, SQL 로그 민감정보 노출 점검.

## 1) Work Summary
- bounded feedback round로 backend의 JDBC 반영 상태를 검토하고 DBA 산출물을 동기화했다.
- 이번 라운드는 신규 엔터티 추가 없이 `tasks` 스키마 일관성 확보와 운영 리스크 재분류에 집중했다.

## 2) Feedback Delta
- 수정한 항목:
  - migration DDL 타입/함수 표현을 runtime 스키마와 동일한 형태로 조정.
- 해결된 리스크:
  - "인메모리만 사용" 리스크는 기본값 `jdbc` 전환으로 완화됨.
- 남은 리스크:
  - migration 체계 이원화(`schema.sql` + `db/migration`)로 drift 재발 가능.

## 3) Table / Column / Index (Current Baseline)
- `tasks(id UUID PK, title VARCHAR(200), description VARCHAR(2000), status VARCHAR(16), created_at TIMESTAMP WITH TIME ZONE, updated_at TIMESTAMP WITH TIME ZONE)`
- 제약조건:
  - `ck_tasks_title_not_blank`
  - `ck_tasks_status IN ('PENDING','DONE')`
  - `ck_tasks_updated_gte_created`
- 인덱스:
  - `idx_tasks_created_at_id(created_at, id)` for list 정렬 경로.

## 4) Transaction / Consistency Considerations
- 현재 CRUD는 단일 row 단위라 `READ COMMITTED`로 충분.
- `save`가 update-then-insert 패턴이므로 고경합 환경에서는 unique conflict 재시도 처리 검토 필요.
- `created_at`은 불변이며 `updated_at`은 상태 변경 시 갱신되어야 함.

## 5) Migration / Rollback Strategy
- `V1__create_tasks.sql`은 여전히 create-only(non-destructive).
- rollback SQL은 data-destructive이므로 운영 승인 없는 자동 실행 금지.
- 다음 단계 권고:
  - migration 단일 실행 체계 확정(Flyway 권장).
  - 확정 후 `schema.sql`과 migration의 중복 제거.

## 6) Validation Results
- 엔터티-저장 구조 정합성: pass
- 인덱스/제약 목적 명확성: pass
- destructive migration 안전성: pass (`V1` non-destructive + rollback 명시)
- feedback round 규칙 준수(변경/해결/잔여 리스크 분리): pass
