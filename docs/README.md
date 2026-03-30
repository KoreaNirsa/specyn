# 📚 Specyn 문서 허브

이 디렉터리는 **도입, 실습, 구조 이해**에 필요한 문서를 모아둔 곳입니다.  
처음 보시는 경우에는 아래 순서대로 읽어보시면 흐름을 잡기 훨씬 수월합니다.

## 추천 읽기 순서

| 순서 | 문서 | 언제 읽으면 좋은가요? |
|---|---|---|
| 1 | [quickstart.md](quickstart.md) | 저장소를 막 열어본 직후입니다. |
| 2 | [playbook.md](playbook.md) | 학습용/파일럿/현업 적용 경로를 나눠 보고 싶을 때입니다. |
| 3 | [architecture.md](architecture.md) | 컴포넌트 책임과 전체 흐름을 이해하고 싶을 때입니다. |
| 4 | [agent-catalog.md](agent-catalog.md) | 어떤 Agent가 무엇을 맡는지 알고 싶을 때입니다. |
| 5 | [sdd-principles.md](sdd-principles.md) | 직접 spec bundle을 작성해 보려 할 때입니다. |
| 6 | [operations.md](operations.md) | 실행 모드, 환경 변수, CI 흐름을 확인할 때입니다. |
| 7 | [prompt-engineering.md](prompt-engineering.md) | prompt/handoff 품질 기준을 정리하고 싶을 때입니다. |
| 8 | [troubleshooting.md](troubleshooting.md) | 실행 중 막혔을 때입니다. |

## 문서 지도

| 문서 | 핵심 내용 | 관련 원본 문서 |
|---|---|---|
| [quickstart.md](quickstart.md) | 실패 가능성이 낮은 첫 실행 경로 | `docs/00-quickstart.md` |
| [playbook.md](playbook.md) | 초급~고급 적용 시나리오 | `docs/08-playbooks.md` |
| [architecture.md](architecture.md) | 전체 구조와 컴포넌트 책임 | `docs/01-architecture.md` |
| [agent-catalog.md](agent-catalog.md) | Agent 분류, 흐름, loop 설계 | `docs/03-agent-flow.md`, `agents/*` |
| [sdd-principles.md](sdd-principles.md) | spec bundle 작성 원칙 | `docs/02-spec-driven-development.md` |
| [operations.md](operations.md) | 실행 모드, 환경 변수, CI | `docs/05-operations.md`, `.env.example`, workflow |
| [prompt-engineering.md](prompt-engineering.md) | prompt/handoff/guardrail 원칙 | `docs/06-prompt-engineering.md` |
| [troubleshooting.md](troubleshooting.md) | 자주 발생하는 문제와 해결 순서 | `docs/09-troubleshooting.md` |

## docs와 guide는 어떻게 나뉘나요?

| 디렉터리 | 용도 |
|---|---|
| `docs` | 처음 도입하거나 실제로 적용해 보는 팀을 위한 문서입니다. |
| `guide` | 운영, 유지보수, 추적성, 확장 전략처럼 더 깊은 실무 가이드를 위한 문서입니다. |

운영자나 메인테이너 관점의 상세 문서는 [../guide/README.md](../guide/README.md)에서 이어서 보실 수 있습니다.

## 참고

기존의 `docs/00~12` 번호 문서도 그대로 유지되어 있습니다.  
새로 정리한 문서는 **처음 읽기 좋은 경로**를 제공하기 위한 별도 레이어라고 보시면 됩니다.
