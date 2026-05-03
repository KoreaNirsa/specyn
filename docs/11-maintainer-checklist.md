# 11. Maintainer Checklist

오픈소스 AX Builder의 메인테이너 관점에서는 **새 기능 추가보다도 실행 안정성, 계약 호환성, 문서 일관성**이 더 중요하다.

## 릴리즈 전 체크 흐름

```text
spec/template change
  -> example spec sync
  -> agent docs sync
  -> validator/test sync
  -> README/docs sync
  -> cross-platform command check
  -> zip/package sanity check
```

## 1. 계약 호환성

- `specs/templates`를 바꿨으면 `specs/001-sample-service`도 같이 갱신했는가
- `plan.md` metadata를 바꿨으면 Python/Backend validator가 함께 갱신되었는가
- Prompt 계약을 바꿨으면 Agent 문서와 Prompt Builder가 같이 반영되었는가
- 기존 사용자의 spec bundle이 불필요하게 깨지지 않는가

## 2. 실행 안정성

- `bootstrap -> doctor -> validate-spec -> compile-prompts -> run-sim`이 유지되는가
- Windows와 Linux 경로 문법이 문서에 모두 반영되었는가
- Docker/Gradle/Codex가 없는 최소 환경에서도 기본 검증 경로는 동작하는가
- feedback loop 추가로 prompt 파일명이 충돌하지 않는가

## 3. 문서 품질

- README와 docs의 시작 경로가 일관되는가
- 새 개념이 들어오면 예제와 ASCII 흐름도가 함께 있는가
- 초급 사용자도 따라갈 수 있는 명령 예시가 있는가
- 고급 사용자용 확장 포인트와 주의 사항이 있는가

## 4. Agent 품질

- 새 Agent를 추가했다면 정의 문서가 존재하는가
- handoff, validation, stop 조건이 문서에 있는가
- bounded feedback round 시 행동 원칙이 있는가
- domain neutrality를 유지하는가

## 5. 향후 대시보드/트레이스 준비

향후 아래 기능이 추가될 것을 감안해 구조를 유지한다.

- agent timeline
- feedback loop trace
- artifact catalog
- run history
- prompt snapshot browser
- reviewer decision audit

따라서 메인테이너는 가능한 한 **명시적 step label**, **결정 근거**, **검증 상태**, **재시도 사유**를 남기는 방향으로 기능을 확장해야 한다.
