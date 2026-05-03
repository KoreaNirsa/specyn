# 02. Spec Driven Development

## Specyn에서 spec-first가 중요한 이유

Specyn은 코드 생성 전에 제품/계약/테스트/리뷰/실행 흐름을 먼저 고정해 drift를 줄인다.
특히 Spec Kit의 `plan.md`는 단순 설명서가 아니라 **실제 multi-agent 실행 흐름**의 기준점이다.

## core spec

아래 5개는 필수다.

- `spec.md`
- `api.md`
- `tasks.md`
- `review.md`
- `plan.md`

## 각 spec의 역할

| spec | 역할 |
|---|---|
| spec.md | 문제 정의, 사용자, 시나리오, NFR, 제외 범위 |
| api.md | endpoint, schema, error contract, 운영 제약, 구조 규칙(`global/common/domain`) |
| tasks.md | 성공/실패/검증/coverage 기준 |
| review.md | release 품질 기준, blocker / major / minor 규칙 |
| plan.md | 어떤 agent를 어떤 순서로 실행할지, handoff/stop/retry 규칙, feedback loop 상한 |

## 공통 요구사항

- YAML front matter
- `목적`
- `입력`
- `출력`
- `실행 규칙`
- `Validation 기준`
- `Prompt`
- Prompt 내부에 `Role`, `Instructions`, `Format`

## spec 상호작용에서 중요한 점

1. `spec.md`는 downstream spec의 어휘와 제약을 고정한다.
2. `api.md`는 Backend/Frontend/Test/Docs가 함께 쓰는 계약이다.
3. `tasks.md`와 `review.md`는 생성 이후 품질 게이트 역할을 한다.
4. `plan.md`는 실제 multi-agent 흐름을 정의하므로 실행 코드와 정합해야 한다.
5. spec 간 `depends_on`은 실제 bundle 안에서 해석 가능해야 한다.

6. `api.md`는 Spring Boot `global / common / domain` 또는 FastAPI `app/global / app/common / app/domain` 구조 힌트를 포함하는 편이 좋다.
7. `plan.md`의 `feedback_loops`와 `max_feedback_rounds`를 사용하면 bounded multi-agent collaboration을 설계할 수 있다.

## 새 spec bundle 생성

### Linux / macOS
```bash
python3 specyn.py init-spec \
  --project-id sample-service \
  --output-dir specs/001-sample-service
```

### Windows (PowerShell)
```powershell
python specyn.py init-spec `
  --project-id sample-service `
  --output-dir specs/001-sample-service
```

## 실행 전 체크

### Linux / macOS
```bash
python3 specyn.py validate --spec-dir specs/001-sample-service
```

### Windows (PowerShell)
```powershell
python specyn.py validate --spec-dir specs/001-sample-service
```

## 좋은 spec의 특징

- 사람이 읽기 쉬우면서 agent가 해석하기 쉬운 구조를 가진다.
- acceptance criteria가 검증 가능하다.
- 예외/보안/운영 제약을 숨기지 않는다.
- 특정 예제 도메인에 과도하게 묶이지 않는다.
