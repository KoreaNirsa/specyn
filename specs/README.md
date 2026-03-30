# specs

Specyn 의 모든 실행은 Markdown spec bundle 에서 시작합니다.

## 1. 필수 spec 파일

- `product.md`
- `api.md`
- `test.md`
- `review.md`
- `agent.md`

## 2. 공통 작성 규칙

모든 spec 은 아래를 기본으로 포함하는 편이 좋습니다.

- YAML front matter
- `목적`
- `입력`
- `출력`
- `실행 규칙`
- `Validation 기준`
- `Prompt`

Prompt 는 가능하면 RIF 구조를 유지합니다.

- `Role`
- `Instructions`
- `Format`

## 3. 문법 검증에서 확인하는 것

`python specyn.py validate --spec-dir ...` 는 아래를 확인합니다.

- 필수 spec 존재 여부
- 필수 섹션 존재 여부
- Prompt 의 RIF 구조
- `product.md` 의 핵심 시나리오 / 비기능 요구사항 / 제외 범위
- `api.md` 의 endpoint 표 / request-response 예시 / 오류 정책
- `test.md` 의 테스트 시나리오 수
- `review.md` 의 구조/보안/테스트/운영 기준
- `agent.md` 의 execution flow / feedback loops / 필수 agent / 정합성

## 4. 포함된 예제 bundle

| 경로 | 용도 |
|---|---|
| `specs/examples/todo-service` | 최소 예제 bundle |
| `specs/projects/sample-service` | `compile-prompts` 다음 단계인 `specyn.py run` 까지 실제로 확인하는 reference CRUD bundle |

## 5. sample-service 를 참고하는 이유

`sample-service` 는 단순 예제가 아니라 아래 목적을 함께 만족하도록 작성되어 있습니다.

1. 사용자가 `run` 까지 실행해 실제 generated 결과를 확인할 수 있다.
2. product/api/test/review/agent spec 를 어떻게 써야 하는지 참고할 수 있다.
3. frontend/backend/ai-server/docs 가 함께 갱신되는 구조를 볼 수 있다.

자세한 설명은 [../docs/sample-service-reference.md](../docs/sample-service-reference.md) 를 참고하세요.

## 6. 새 프로젝트를 시작하는 방법

### 새 spec bundle 생성

```powershell
python specyn.py init-spec --project-id my-service --output-dir specs/projects/my-service
```

### 추천 작업 순서

1. `sample-service` 를 읽어 구조와 수준을 확인한다.
2. 새 bundle 을 만든다.
3. `product.md` 에 목표/시나리오/NFR/제외 범위를 먼저 적는다.
4. `api.md` 에 endpoint 표와 예시를 적는다.
5. `test.md`, `review.md`, `agent.md` 를 채운다.
6. `validate -> compile-prompts -> run` 순으로 확인한다.

## 7. sample-service 기준 전체 예시

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

그 다음 `http://localhost:5173/generated/sample-service` 에서 실제 CRUD 흐름을 확인합니다.
