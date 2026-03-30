# 🛡 메인테이너 가이드

이 문서는 저장소를 유지보수하는 관점에서 **무엇을 바꾸면 어디까지 같이 확인해야 하는지**를 정리합니다.

## 1. 변경 영향도 매트릭스

| 변경한 것 | 함께 확인할 것 |
|---|---|
| `specs/templates` | `specs/examples`, validator, docs |
| `agents/*.md` | prompt compiler, 실행 흐름 문서, 예제 bundle |
| `scripts/`, `specyn.py` | README 명령어, docs/quickstart, Windows/Linux 예시 |
| `backend/` | workflow backend job, API 문서, health check |
| `ai-server/` | 환경 변수, endpoint 문서, Codex/RAG 흐름 |
| `frontend/` | `VITE_*` 환경 변수, README 캡처/설명, build job |
| `docs/`, `guide/` | README 링크, 문서 허브, legacy 문서 대응 |

## 2. 릴리즈 전 최소 체크

1. `bootstrap -> doctor -> validate-spec -> compile-prompts -> run-sim`
2. `make ci-local`
3. docs 링크/이미지 경로 확인
4. 예제 spec bundle validate 확인
5. workflow 영향도 확인

## 3. 문서 동기화 원칙

- README는 **첫 진입 경로**만 간결하게 보여주는 편이 좋습니다.
- 자세한 설명은 `docs/`와 `guide/`로 넘기고, README에서 중복 설명은 줄이는 편이 좋습니다.
- 기존 번호 문서를 유지하더라도, 새로 정리한 문서 세트와 링크가 어긋나지 않도록 관리하는 편이 좋습니다.

## 4. CI 관점에서 체크할 것

현재 GitHub Actions는 아래 job을 사용합니다.

| Job | 체크 내용 |
|---|---|
| `backend` | Gradle test |
| `python` | spec check, pytest, ruff format |
| `frontend` | npm install, typecheck, build |

즉, 어떤 변경이든 **문서만 바뀌어 보이더라도 실제로는 세 계층 모두와 엮일 수 있다**는 점을 염두에 두는 편이 좋습니다.

## 5. 패키징/배포 전 체크

- zip 배포 시 루트 구조가 유지되는가
- `docs/assets` 이미지가 함께 포함되는가
- Windows 사용자가 압축을 풀고 바로 quickstart를 따라갈 수 있는가
- `.env.example`과 README 설명이 어긋나지 않는가
