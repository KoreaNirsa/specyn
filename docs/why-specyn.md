# 💡 왜 Specyn인가요?

이 문서는 “왜 또 다른 AI 개발 도구가 필요한가요?”라는 질문에 답합니다.

## 1. Specyn이 풀고 싶은 문제

팀이 AI를 활용해 개발할 때 자주 마주치는 문제는 비슷합니다.

1. 프롬프트와 기준이 채팅창 안에만 남아 재현하기 어렵습니다.
2. 코드 생성은 됐는데 문서, 테스트, 운영 메모가 따로 움직입니다.
3. 누가 어떤 기준으로 승인했는지 trace가 약합니다.
4. 데모는 멋있지만 팀 표준으로 쓰기 어려운 경우가 많습니다.

Specyn은 이 지점을 **spec bundle + agent flow + generated artifacts + run trace** 로 묶어 해결하려고 합니다.

## 2. Specyn의 핵심 약속

### spec-first

코드보다 spec bundle을 먼저 둡니다.

- `product.md`
- `api.md`
- `test.md`
- `review.md`
- `agent.md`

즉, “무엇을 만들지”와 “어떤 기준으로 통과시킬지”를 먼저 문서화합니다.

### agent-visible

누가 어떤 순서로 참여하는지 `agent.md` 에서 보입니다.

```text
planner -> design -> api -> backend -> frontend -> ... -> final-review
```

feedback loop도 숨기지 않고 spec에 명시합니다.

### runnable

샘플 프로젝트는 단순 텍스트 예제가 아니라, `run` 이후 바로 확인 가능한 CRUD 데모여야 합니다.

즉, 사용자는 “설명만 읽는 경험”이 아니라 “직접 실행해서 결과를 보는 경험”을 얻습니다.

### reviewable

Specyn은 generated code만 남기지 않고 아래도 함께 남깁니다.

- prompt 출력
- run manifest / step trace
- generated docs
- OpenAPI
- test plan

그래서 팀 단위 리뷰와 회고에 더 적합합니다.

## 3. 어떤 팀에 잘 맞나요?

| 팀/상황 | 잘 맞는 이유 |
|---|---|
| 플랫폼 팀 | spec과 실행 규약을 표준화하기 좋습니다. |
| 백엔드/풀스택 팀 | API, docs, tests, generated 결과를 함께 다루기 쉽습니다. |
| 교육/부트캠프 | spec → run → dev 결과를 한 번에 보여주기 좋습니다. |
| 사내 AX Builder 추진 팀 | 로컬 runtime과 Codex runtime을 함께 실험하기 좋습니다. |

## 4. 무엇을 목표로 하지 않나요?

Specyn은 아래를 지금 당장 전부 해결한다고 말하지 않습니다.

- 모든 도메인에 최적화된 완성형 코드 생성기
- human review 없이 바로 운영 배포되는 완전자율 시스템
- 특정 모델/벤더에 강하게 종속된 프레임워크
- IDE 안에서만 쓰는 개인용 agent 도구

즉, Specyn은 **개인 생산성 도구**보다 **팀 표준과 재현성** 쪽에 더 가깝습니다.

## 5. 왜 sample-service 같은 작은 CRUD 샘플이 중요한가요?

처음 보는 사용자는 거대한 도메인보다 **작고 끝까지 확인 가능한 reference sample** 에서 더 빨리 신뢰를 얻습니다.

sample-service 는 아래 역할을 동시에 합니다.

- spec 작성 수준의 기준 예시
- generated 산출물 확인 예시
- docs/guide 검증 기준
- quickstart 성공 경험

즉, “실제로 실행된다”는 인상을 가장 빨리 주는 기준점입니다.

## 6. 장기적으로 어디를 향하나요?

Specyn의 장기 방향은 아래와 같습니다.

1. **오픈 SDD reference framework**
2. **팀이 합의 가능한 agent workflow standard**
3. **spec, docs, tests, artifacts를 묶는 delivery contract**
4. **Codex/Copilot/사내 agent 실행기를 연결하는 공통 기반**

이 방향을 더 구체적으로 보려면 [comparison.md](comparison.md), [../guide/roadmap.md](../guide/roadmap.md), [../guide/community-growth.md](../guide/community-growth.md) 를 함께 보는 편이 좋습니다.
