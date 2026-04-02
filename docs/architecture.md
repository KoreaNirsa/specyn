# 아키텍처 개요

Specyn은 제어면과 실행면을 분리해 spec 기반 개발 흐름을 관리합니다.

## 주요 구성요소

| 구성요소 | 역할 | 현재 경로 |
|---|---|---|
| Dashboard Frontend | spec 입력, 실행 요청, 상태 확인 UI | `dashboard/frontend/` |
| Dashboard Backend | spec 검증, 실행 계획 정리, 결과 집계 | `dashboard/backend/` |
| AI Server | prompt 조합, OpenAI 호출, Codex 실행, RAG 보조 | `dashboard/ai-server/` |
| CLI | setup, doctor, validate, compile-prompts, run | `specyn.py` |
| Host Helper | 로컬 프로세스 직접 실행용 보조 도구 | `scripts/specyn_tasks.py` |
| Agent 정의 | 역할, handoff, validation 규칙 | `agents/` |
| Spec Bundle | product/api/test/review/agent 정의 | `specs/` |
| Workspace / Artifacts | prompt, 실행 로그, 생성 산출물 | `.specyn/`, `.workspace/`, `projects/` |
| CI | Python, backend, frontend 검증 | `.github/workflows/` |

## 권장 실행 흐름

```text
specs/templates 또는 specs/projects/sample-service
  -> python specyn.py validate
  -> python specyn.py compile-prompts
  -> python specyn.py run
  -> projects/<project-id> 생성물 검토
  -> 필요 시 sample-up 또는 sample-dev 로 런타임 검증
```

## 왜 이 구조인가

- spec 가 코드보다 먼저 정의됩니다.
- 대시보드는 제어면으로 동작하고, 실제 생성/실행은 backend 와 AI server 가 맡습니다.
- sample-service 는 템플릿 응용 예시이자 validator, prompt compiler, runtime 검증 기준본 역할을 합니다.
- 배포 대상은 주로 `dashboard/*` 와 `projects/*` 생성물이며, CLI 와 helper 는 이를 지원하는 코어 도구입니다.

## 생성 산출물 구조 규약

- Spring Boot: `global / common / domain`
- FastAPI: `app/global / app/common / app/domain`
- Frontend: `src/generated/<project-id>/` 또는 프로젝트별 독립 frontend

이 규약은 template, sample-service, generated project 가 서로 같은 기준을 공유하도록 하기 위한 것입니다.
