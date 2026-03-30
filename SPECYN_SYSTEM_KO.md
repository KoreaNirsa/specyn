# Specyn 시스템 설계서 (한국어)

## 1. 프로젝트 목적

Specyn은 다음 목적을 가진 오픈소스 AX Builder 프레임워크다.

1. Spec Driven Development를 위한 기본 템플릿 제공
2. clone 후 즉시 검증 가능한 실행 뼈대 제공
3. 특정 도메인에 묶이지 않는 agent/spec 구조 제공
4. 처음 접하는 사용자도 문서만 읽고 따라갈 수 있는 진입점 제공
5. production-oriented prompt engineering 구조 제공
6. CI 범위까지 포함하고, 운영/CD는 확장 포인트로 남김
7. 향후 대시보드, 에이전트 추적, run history로 확장 가능한 구조 유지

## 2. 핵심 구조

```text
Frontend / CLI
  -> Backend Orchestrator
  -> AI Server
  -> Workspace / Artifacts
  -> Review / Docs / Final Review
```

## 3. 필수 spec

- `product.md`
- `api.md`
- `test.md`
- `review.md`
- `agent.md`

`agent.md`는 실제 multi-agent 실행 순서를 결정하는 문서다.

## 4. 기본 agent 카탈로그

- Planner
- Design
- API
- Backend
- Frontend
- DBA
- DevOps
- Test
- Code Analysis
- Security
- Performance
- Review
- Docs
- Final Review
- RAG(optional)
- Orchestrator

## 5. 기본 실행 전략

초기 진입은 아래 검증 흐름을 우선한다.

```bash
make bootstrap
make doctor
make validate-spec
make compile-prompts
make run-sim
```

전체 스택은 그 다음 `make dev` 또는 Docker Compose로 올린다.

## 6. 확장 방향

- queue 기반 비동기 실행
- artifact/audit 저장소 연동
- branch-per-run / PR bot
- dashboard / agent trace / execution analytics
