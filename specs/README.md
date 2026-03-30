# specs

모든 Specyn 실행은 Markdown spec bundle에서 시작합니다.

## 필수 spec

- `product.md`
- `api.md`
- `test.md`
- `review.md`
- `agent.md`

## 공통 규칙

- YAML front matter 포함
- `목적`, `입력`, `출력`, `실행 규칙`, `Validation 기준`, `Prompt` 섹션 포함
- Prompt는 RIF(Role / Instructions / Format) 구조 권장
- `api.md`에는 구조 규칙(Spring Boot `global/common/domain`, FastAPI `app/global/common/domain`)을 넣는 편이 좋음
- `agent.md`에는 `execution_flow`, `supported_agents`, `optional_agents`를 명시
- bounded feedback loop가 필요하면 `feedback_loops`와 `max_feedback_rounds`를 명시

## 포함된 예제 번들

| 경로 | 용도 |
|---|---|
| `specs/examples/todo-service` | 최소 예제 bundle |
| `specs/projects/sample-service` | `compile-prompts` 이후 `specyn run`까지 이어지는 fuller example bundle |

## 스펙 문법 검증에서 체크하는 것

`python specyn.py validate --spec-dir ...` 는 아래 항목을 함께 확인합니다.

- 필수 spec 존재 여부
- 필수 섹션 존재 여부
- Prompt의 RIF 구조
- `product.md`의 시나리오/NFR/제외 범위
- `api.md`의 엔드포인트 표, Request/Response 예시, 오류 정책
- `test.md`의 테스트 시나리오 수
- `review.md`의 구조/보안/테스트/운영 규칙 수
- `agent.md`의 필수 agent, feedback loop, 실행 순서

## 빠른 시작

### Linux / macOS

```bash
python3 specyn.py validate --spec-dir specs/projects/sample-service
python3 specyn.py compile-prompts \
  --spec-dir specs/projects/sample-service \
  --output-dir .specyn/prompts/sample-service \
  --workspace .workspace/sample-service
python3 specyn.py run \
  --spec-dir specs/projects/sample-service \
  --project-id sample-service \
  --workspace .workspace/sample-service
```

### Windows (PowerShell)

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
```
