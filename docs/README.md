# 📚 Specyn 문서 허브

이 디렉터리는 **실제 사용자가 순서대로 따라가며 `specyn.py run` 까지 실행하고 결과를 확인할 수 있도록** 정리한 문서 모음입니다.

## 가장 추천하는 읽기 순서

| 순서 | 문서 | 목적 |
|---|---|---|
| 1 | [quickstart.md](quickstart.md) | 가장 짧고 안전한 첫 실행 경로 |
| 2 | [playbook.md](playbook.md) | `compile-prompts` 다음 단계부터 전체 SDD 흐름 이해 |
| 3 | [cli-run-reference.md](cli-run-reference.md) | `specyn.py run` 명령과 옵션을 정확히 이해 |
| 4 | [sample-service-reference.md](sample-service-reference.md) | 샘플 CRUD 프로젝트와 spec bundle을 참고용으로 활용 |
| 5 | [operations.md](operations.md) | 실행 모드, 환경 변수, 운영 포인트 확인 |
| 6 | [troubleshooting.md](troubleshooting.md) | 막혔을 때 빠르게 복구 |
| 7 | [04-codex-execution.md](04-codex-execution.md) | Codex 실행 환경까지 확장 |

## 문서 역할 요약

| 문서 | 핵심 내용 |
|---|---|
| [quickstart.md](quickstart.md) | bootstrap → doctor → validate → compile-prompts → run → dev → 결과 확인 |
| [playbook.md](playbook.md) | CLI 기반 실행과 Codex 실행 환경을 모두 비교 |
| [cli-run-reference.md](cli-run-reference.md) | `run` 명령의 옵션, 실행 모드, 산출물, 예시 |
| [sample-service-reference.md](sample-service-reference.md) | sample-service spec bundle의 목적과 파일별 참고 포인트 |
| [operations.md](operations.md) | 실행 모드, 주요 환경 변수, CI/운영 메모 |
| [troubleshooting.md](troubleshooting.md) | 로컬 런타임/Codex 모드 공통 문제 해결 |

## `docs` 와 `guide` 의 차이

| 디렉터리 | 용도 |
|---|---|
| `docs` | 처음 실행하고 적용하는 사람을 위한 문서 |
| `guide` | 운영, 유지보수, 로컬 개발, 추적성, 장기 확장 가이드 |

운영/메인테이너 관점으로 이어서 보려면 [../guide/README.md](../guide/README.md) 를 참고하세요.

## 번호형 문서에 대하여

`00~12` 번호 문서는 기존 구조를 유지하기 위해 남겨 둔 레퍼런스 문서입니다. 실제 실행 흐름은 위 표의 문서 집합을 우선 기준으로 사용하면 됩니다.
