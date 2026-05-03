# 📝 SDD(Spec Driven Development) 작성 원칙

Specyn에서 spec는 단순한 설명 문서가 아니라 **실행과 검증의 기준점**입니다.

## 1. 왜 spec-first가 중요한가요?

Specyn은 코드 생성 전에 제품/계약/테스트/리뷰/실행 흐름을 먼저 고정해 drift를 줄입니다.  
특히 Spec Kit의 `plan.md`는 단순 안내문이 아니라 실제 multi-agent 실행 흐름의 기준이 됩니다.

## 2. core spec bundle

아래 5개는 기본적으로 준비하는 편이 좋습니다.

| 파일 | 역할 |
|---|---|
| `spec.md` | 문제 정의, 사용자, 시나리오, NFR, 제외 범위 |
| `api.md` | endpoint, schema, error contract, 운영 제약, 구조 규칙 |
| `tasks.md` | 성공/실패 시나리오, coverage 기준, 검증 우선순위 |
| `review.md` | blocker / major / minor 기반 리뷰 기준 |
| `plan.md` | Agent 실행 순서, handoff, stop/retry, feedback loop 규칙 |

## 3. 공통 작성 규칙

| 항목 | 설명 |
|---|---|
| YAML front matter | 문서 메타데이터를 명시합니다. |
| 목적 | 이 spec가 해결하려는 일을 적습니다. |
| 입력 | 어떤 정보가 들어오는지 정리합니다. |
| 출력 | 어떤 산출물을 기대하는지 적습니다. |
| 실행 규칙 | 처리 규칙, 제한, 예외를 정리합니다. |
| Validation 기준 | 통과/실패 기준을 적습니다. |
| Prompt | Agent가 해석할 수 있는 지시문을 포함합니다. |

Prompt 내부에는 가능하면 `Role`, `Instructions`, `Format`을 분리해 적는 편이 좋습니다.

## 4. Spec 간 상호작용에서 중요한 점

1. `spec.md`는 전체 어휘와 범위를 고정합니다.
2. `api.md`는 Backend, Frontend, Test, Docs가 함께 보는 계약이 됩니다.
3. `tasks.md`와 `review.md`는 생성 이후 품질 게이트 역할을 합니다.
4. `plan.md`는 실제 multi-agent 실행 그래프를 정의하므로 실행 코드와 정합해야 합니다.
5. `depends_on`이 있다면 bundle 안에서 실제로 해석 가능해야 합니다.

## 5. bundle 구조 예시

```text
specs/001-sample-service
├── spec.md
├── api.md
├── tasks.md
├── review.md
├── plan.md
└── contracts/
```

실행 가능한 reference sample은 `specs/001-sample-service`에서 바로 확인하실 수 있습니다.

## 6. 새 spec bundle 생성하기

### Linux / macOS

```bash
python3 specyn.py init-spec   --project-id my-service   --output-dir specs/003-my-service
```

### Windows (PowerShell)

```powershell
python specyn.py init-spec `
  --project-id my-service `
  --output-dir specs/003-my-service
```

## 7. 실행 전 검증하기

### Linux / macOS

```bash
python3 specyn.py validate --spec-dir specs/001-sample-service
```

### Windows (PowerShell)

```powershell
python specyn.py validate --spec-dir specs/001-sample-service
```

## 8. 좋은 spec의 특징

| 좋은 예 | 피하고 싶은 예 |
|---|---|
| 사람이 읽기 쉽고 Agent도 해석하기 쉬운 구조입니다. | 설명이 길지만 실행 기준이 모호합니다. |
| 필수/선택 범위가 분명합니다. | 해야 할 일과 하지 말아야 할 일이 섞여 있습니다. |
| validation 기준이 명시적입니다. | “잘 동작해야 함”처럼 추상적입니다. |
| 가정과 리스크를 분리해 적습니다. | TODO만 남겨 놓고 책임을 넘깁니다. |

## 9. 실무 팁

- `spec.md`를 충분히 다듬은 뒤 다른 spec를 쓰면 수정 비용이 줄어듭니다.
- `api.md`에 구조 규칙을 녹여두면 Backend/Review 단계가 안정적입니다.
- `plan.md`의 feedback loop는 적을수록 좋고, 필요한 경계에만 두는 편이 낫습니다.
- sample-service에 과적합하지 말고 도메인 중립적인 규칙을 유지해 보시는 것이 좋습니다.

## 10. 함께 보면 좋은 문서

- Agent 흐름: [agent-catalog.md](agent-catalog.md)
- 운영 흐름: [operations.md](operations.md)
- 프롬프트 품질: [prompt-engineering.md](prompt-engineering.md)
