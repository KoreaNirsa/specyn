# 🏗 전체 아키텍처

Specyn은 **제어 plane**과 **실행 plane**을 분리해 생각하면 이해하기 쉽습니다.

<p align="center">
  <img src="assets/specyn-architecture.svg" alt="Specyn architecture overview" width="100%" />
</p>

## 1. 컴포넌트 역할 요약

| 컴포넌트 | 역할 | 현재 저장소 위치 |
|---|---|---|
| React UI | Spec 편집, 실행 요청, 결과 요약 | `frontend/` |
| CLI / Scripts | bootstrap, doctor, validate, compile, run | `specyn.py`, `scripts/` |
| Spring Boot Backend | spec 검증, 실행 흐름 계획, 결과 집계 | `backend/` |
| FastAPI AI Server | prompt 조합, OpenAI 호출, Codex 실행, RAG 검색 | `ai-server/` |
| Agent 정의 | 역할, handoff, validation 규칙 | `agents/` |
| Spec Bundle | 제품/계약/테스트/리뷰/에이전트 흐름 정의 | `specs/` |
| Workspace / Artifacts | prompt, 코드, 테스트, 문서 산출물 | `.specyn/`, `.workspace/` |
| CI | backend/python/frontend 검증 | `.github/workflows/ci.yml`, `ci/` |

## 2. Plane 기준으로 보기

| Plane | 포함 요소 | 책임 |
|---|---|---|
| 제어 plane | UI, CLI, Spring Boot Backend, Spec Validator | 무엇을 어떤 순서로 실행할지 결정합니다. |
| 실행 plane | FastAPI AI Server, Codex, Optional RAG, Workspace | 실제 prompt 실행과 산출물 생성을 담당합니다. |
| 검증 plane | Test, Review, Docs, CI | 생성 결과가 품질 기준을 만족하는지 확인합니다. |

## 3. 데이터 흐름

```text
Frontend / CLI
  -> Spec bundle 수집
  -> Backend validation
  -> plan.md 기반 workflow planning
  -> AI Server prompt execution
  -> Workspace / Artifacts 생성
  -> Test / Review / Docs / Final Review
  -> 결과 요약 및 CI 검증
```

## 4. 왜 Spring Boot + FastAPI + React인가요?

| 계층 | 선택 이유 |
|---|---|
| Spring Boot | 오케스트레이션, 검증, 운영 API 계층을 안정적으로 구성하기 좋습니다. |
| FastAPI | AI 실행, prompt composition, Codex/RAG 연동을 빠르게 다루기 좋습니다. |
| React(Vite) | spec 입력과 결과 확인 UI를 빠르게 실험하기 좋습니다. |

## 5. Specyn이 중요하게 보는 설계 원칙

1. **Spec가 코드보다 상위의 진실(source of truth)** 입니다.
2. Agent는 단일 책임을 가지는 편이 유지보수에 유리합니다.
3. 생성과 검증을 분리해야 drift를 줄일 수 있습니다.
4. feedback loop는 필요한 경계에만 bounded하게 두는 편이 좋습니다.
5. CI까지는 기본 제공하되, CD와 인프라는 확장 포인트로 남기는 편이 안전합니다.

## 6. 생성 대상 애플리케이션 구조 규약

Specyn은 생성 대상 애플리케이션 구조로 아래 방향을 권장합니다.

```text
Spring Boot
  -> global / common / domain

FastAPI / LangChain
  -> app/global / app/common / app/domain
```

이 규약을 `api.md`에 미리 녹여두면 Backend, Frontend, Review Agent가 같은 기준으로 판단하기 쉬워집니다.

## 7. 배포/확장 방향

| 환경 | 확장 포인트 |
|---|---|
| 로컬 | `make dev`, `make ai-server`, `make backend`, `make frontend` |
| Docker Compose | `docker-compose.local.yml` 기반 통합 실행 |
| 온프레미스 | 내부 Git, secret manager, artifact 저장소와 연동 |
| Kubernetes | backend / ai-server / frontend를 개별 deployment로 분리 |
| 클라우드 | ECS/Fargate, EKS, object storage, queue, telemetry로 확장 |

## 8. 함께 보면 좋은 문서

- 빠르게 실행해 보고 싶다면 [quickstart.md](quickstart.md)
- Agent 책임을 보려면 [agent-catalog.md](agent-catalog.md)
- 운영/배포 관점은 [operations.md](operations.md)
- 장기 확장 계획은 [../guide/roadmap.md](../guide/roadmap.md)
