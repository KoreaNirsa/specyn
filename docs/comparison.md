# ⚖️ Specyn은 다른 접근과 어떻게 다른가요?

이 문서는 Specyn을 템플릿 저장소, 코드 생성기, IDE agent, 사내 플랫폼 템플릿과 비교해 봅니다.

## 1. 한눈에 보는 비교

| 접근 | source of truth | agent flow 명시성 | docs/test 동기화 | 실행 가능한 reference sample | 팀 표준화 적합성 |
|---|---|---|---|---|---|
| 템플릿 저장소 | 디렉터리/코드 | 낮음 | 낮음 | 보통 없음 | 중간 |
| 단일 코드 생성기 | 프롬프트/설정 | 낮음 | 낮음~중간 | 드묾 | 낮음 |
| IDE agent 중심 개발 | 대화/편집 맥락 | 낮음 | 낮음 | 개인 데모 중심 | 낮음~중간 |
| 사내 플랫폼 템플릿 | 정책/템플릿 | 중간 | 중간 | 조직별로 다름 | 높음 |
| **Specyn** | **Markdown spec bundle** | **높음 (`agent.md`)** | **높음** | **기본 포함** | **높음** |

## 2. 템플릿 저장소와 비교하면

템플릿 저장소는 시작 속도가 빠르지만, 아래가 약해지기 쉽습니다.

- 왜 이 구조인지에 대한 spec 근거
- agent handoff와 검증 trace
- docs/test/generated 결과의 동기화

Specyn은 템플릿만 제공하는 대신, **spec → execution flow → generated artifacts** 를 묶어 둡니다.

## 3. 단일 코드 생성기와 비교하면

단일 코드 생성기는 빠르지만, 다음 문제가 남기 쉽습니다.

- 어떤 단계에서 누가 무엇을 검토했는지 불명확
- 테스트/리뷰 문서가 뒤늦게 붙음
- 팀 표준으로 재사용하기 어려움

Specyn은 `test.md`, `review.md`, `agent.md` 를 같이 두어 **생성 결과의 품질 기준**을 먼저 정의합니다.

## 4. IDE 안의 agent 경험과 비교하면

IDE agent는 개인 생산성에는 강하지만, 팀 단위 표준화에는 아래 한계가 있습니다.

- 채팅 기반 맥락이 저장소 밖에 남는 경우가 많음
- 실행 그래프가 팀 규약으로 남기 어려움
- 문서/운영/리뷰 기준이 코드와 분리되기 쉬움

Specyn은 저장소 안에서 재현 가능한 spec과 artifacts를 남기는 쪽에 더 무게를 둡니다.

## 5. 사내 플랫폼 템플릿과 비교하면

사내 플랫폼 템플릿은 조직 정합성에 강하지만, 공개 표준이나 외부 기여 친화성은 약할 수 있습니다.

Specyn은 아래 사이를 연결하려고 합니다.

- 사내 표준에 필요한 재현성
- 오픈소스가 필요한 공개성과 참고 가능성
- AI agent 실행기가 필요한 확장성

## 6. Specyn이 특히 강한 지점

1. **spec-first 구조**
2. **agent-visible workflow**
3. **generated docs/OpenAPI/run trace 동시 생성**
4. **로컬 deterministic runtime + Codex runtime 동시 지원**
5. **sample-service 같은 실행 가능한 reference sample 포함**

## 7. 반대로 지금 약한 지점도 있습니다.

공개 표준이 되려면 아래를 계속 보강해야 합니다.

- 더 많은 reference sample
- 공개 benchmark와 사례
- 다중 OS/다중 런타임 smoke CI
- 릴리즈 운영과 거버넌스 성숙도
- 외부 통합 포인트 문서화

## 8. 언제 Specyn이 과할 수 있나요?

아래 상황이라면 더 단순한 도구가 맞을 수 있습니다.

- 개인이 하루 안에 실험용 코드를 급히 뽑아야 할 때
- docs/test/review trace보다 빠른 시제품만 필요할 때
- 팀 표준화보다 IDE 안의 속도가 더 중요한 때

즉, Specyn은 **개인용 one-shot 생성기**보다 **팀 단위 재현 가능한 delivery framework** 에 더 가깝습니다.
