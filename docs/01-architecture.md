# 01. Architecture

Specyn은 **제어 plane**과 **실행 plane**을 분리한다.

## 제어 plane

- Frontend
- Spring Boot Orchestrator
- Agent Registry
- Spec Validator
- CLI / Local Scripts

## 실행 plane

- FastAPI AI Server
- OpenAI Responses Client
- Codex Executor
- Optional RAG Search
- Workspace / Artifacts

## 데이터 흐름

```text
Frontend / CLI
  -> Backend
  -> Spec validation
  -> Workflow planning (execution_flow + feedback_loops)
  -> AI Server
  -> Prompt compilation
  -> Codex execution
  -> Generated files / patches / docs
  -> Validation results
  -> CI targets
```

## 설계 원칙

1. 스펙이 코드보다 상위의 진실(source of truth)이다.
2. Agent는 단일 책임을 가진다.
3. handoff에는 validation 정보가 포함되어야 한다.
4. 생성과 검증을 분리한다.
5. CI 범위까지만 기본 제공하고, CD/인프라는 확장 포인트로 남긴다.


## 생성 대상 애플리케이션 구조 기준

- Spring Boot: `global / common / domain`
- FastAPI / LangChain: `app/global / app/common / app/domain`

프레임워크 런타임 내부 구조와 생성 대상 애플리케이션 구조는 분리해서 볼 수 있다.
