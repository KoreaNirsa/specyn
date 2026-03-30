# sample-service 참고 가이드

`specs/projects/sample-service` 는 단순 placeholder 가 아니라, **Specyn 사용자가 `specyn.py run` 까지 실행했을 때 실제로 확인 가능한 간단한 Task CRUD 웹사이트**를 만들기 위한 reference spec bundle 입니다.

## 1. sample-service 의 목적

sample-service 는 두 역할을 동시에 가집니다.

1. **실행 확인용 샘플**: generated frontend/backend/ai-server/docs 가 함께 갱신되는지 확인
2. **spec 작성 참고용 샘플**: 사용자가 자기 프로젝트 spec bundle 을 작성할 때 베이스로 참고

## 2. sample-service 로 확인할 수 있는 실제 결과

`specyn.py run` 이후:

- Frontend generated CRUD 페이지 생성
- Spring Boot generated CRUD controller 생성
- AI Server generated context route 생성
- OpenAPI / generated docs / test plan 생성

`python scripts/specyn_tasks.py dev` 이후:

- `http://localhost:5173/generated/sample-service`
- `http://localhost:8080/api/v1/tasks`
- `http://localhost:8000/generated/sample-service/context`

## 3. spec 파일별 역할

### `product.md`

무엇을 만들지 정의합니다.

sample-service 에서는 아래를 명확히 적고 있습니다.

- 왜 이 샘플이 필요한지
- 어떤 사용자/개발자가 보는지
- 핵심 CRUD 시나리오
- 비기능 요구사항
- 제외 범위

### `api.md`

실제 generated frontend/backend 가 함께 사용할 계약을 정의합니다.

sample-service 에서는 아래를 포함합니다.

- 엔드포인트 표
- request/response 예시
- 오류 정책
- 보안/운영 제약

### `test.md`

어떤 시나리오를 검증할지 정의합니다.

sample-service 에서는 아래를 커버합니다.

- 생성
- 목록 조회
- 상세 조회
- 상태 변경
- 삭제
- generated frontend manual smoke test

### `review.md`

언제 release-ready 로 볼지에 대한 품질 기준입니다.

sample-service 에서는 아래를 명시합니다.

- placeholder 응답 금지
- 문서/구현 drift 점검
- 보안/오류 응답 기준
- generated UI 확인 기준

### `agent.md`

어떤 Agent 가 어떤 순서로 참여할지 정의합니다.

sample-service 에서는 아래를 볼 수 있습니다.

- `execution_flow`
- `feedback_loops`
- `max_feedback_rounds`
- `supported_agents`
- `optional_agents`

## 4. sample-service 를 내 프로젝트 베이스로 쓰는 방법

### 방법 1. `init-spec` 로 새 bundle 생성 후 직접 옮겨 쓰기

```powershell
python specyn.py init-spec --project-id my-service --output-dir specs/projects/my-service
```

그 다음 sample-service 의 구조를 참고해 각 파일을 채웁니다.

### 방법 2. sample-service 를 복사해 도메인만 교체

초기 파일럿 단계에서는 sample-service 를 복사한 뒤 아래를 순서대로 바꾸는 방식이 빠릅니다.

1. `product.md` 의 비즈니스 배경과 시나리오
2. `api.md` 의 endpoint 표와 예시
3. `test.md` 의 핵심 시나리오
4. `review.md` 의 blocker/major 기준
5. `agent.md` 의 execution flow 와 optional agent

## 5. sample-service 를 보고 꼭 참고할 포인트

- 문서가 실제 실행 결과와 이어져야 합니다.
- `api.md` 의 계약은 generated frontend/backend 와 drift 되면 안 됩니다.
- `agent.md` 는 “어떤 에이전트들이 참여할지”의 source of truth 입니다.
- `review.md` 에는 문서 정합성까지 포함해야 실제 프로젝트에서 덜 흔들립니다.
- sample-service 처럼 “작고 끝까지 확인 가능한 도메인”이 초기 reference spec 으로 가장 좋습니다.

## 6. sample-service 실행 예시

```powershell
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts `
  --spec-dir specs/projects/sample-service `
  --output-dir .specyn/prompts/sample-service `
  --workspace .workspace/sample-service
python specyn.py run `
  --spec-dir specs/projects/sample-service `
  --project-id sample-service `
  --workspace .workspace/sample-service
python scripts/specyn_tasks.py dev
```

그 뒤 `http://localhost:5173/generated/sample-service` 를 열어 CRUD 흐름을 확인합니다.
