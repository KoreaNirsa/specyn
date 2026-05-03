# 🏛 Specyn 거버넌스

이 문서는 Specyn 저장소를 공개 오픈소스로 운영할 때 **누가 어떻게 결정하고, 어떤 변경이 어떤 절차를 거치는지**를 설명합니다.

## 1. 목적

Specyn은 단순한 코드 저장소보다 **오픈 SDD 프레임워크**에 가깝습니다.
그래서 코드 변경뿐 아니라 spec, docs, agent flow, 실행 기준, reference sample까지 함께 다뤄야 합니다.

이 문서의 목적은 아래를 분명히 하는 것입니다.

- 어떤 변경이 바로 PR로 가능하고
- 어떤 변경은 더 큰 합의가 필요하며
- 누가 최종 승인하는지
- 공개 후 어떻게 유지보수할지

## 2. 역할

| 역할 | 책임 |
|---|---|
| Maintainer | 방향성 결정, 리뷰/릴리즈 승인, 커뮤니티 운영 |
| Contributor | 코드, spec, docs, sample, 테스트 기여 |
| Reviewer | 기술/문서/보안/운영 관점의 리뷰 |
| Community member | 사용, 질문, 이슈 제보, 사례 공유 |

초기 단계에서는 **저장소 관리자와 merge 권한 보유자**가 maintainer 역할을 맡습니다.
이후 프로젝트가 커지면 영역별 maintainer를 더 명확히 분리하는 편이 좋습니다.

## 3. 의사결정 방식

### 바로 PR로 가능한 변경

- 오탈자 수정
- 링크 수정
- small bug fix
- sample-service를 깨뜨리지 않는 문서 보강
- 테스트/가드레일 추가

### 합의가 필요한 변경

아래는 이슈 또는 Discussion 성격의 사전 논의를 권장합니다.

- `plan.md` 구조 변경
- spec schema / validator 규칙 변경
- local runtime / Codex runtime 계약 변경
- sample-service 기준 흐름을 깨는 UX/API 변경
- 릴리즈 정책 / 지원 범위 / 라이선스 정책 변경

## 4. RFC에 가까운 변경은 어떻게 하나요?

아래 조건 중 하나에 해당하면 큰 변경으로 봅니다.

- 여러 agent 역할 정의가 함께 바뀐다.
- spec bundle 필수 구조가 달라진다.
- quickstart / sample-flow / dev 확인 절차가 달라진다.
- generated artifact 구조가 크게 바뀐다.

이 경우 권장 흐름은 아래와 같습니다.

1. 이슈 또는 제안 템플릿 생성
2. 문제 정의와 기대 효과 정리
3. 영향을 받는 spec / docs / runtime / sample 정리
4. 작은 단계로 나눈 구현 계획 제시
5. PR로 반영

## 5. 릴리즈 원칙

현재는 빠른 반복이 우선이므로 아래를 기본 원칙으로 둡니다.

- sample-service 기준 quickstart가 살아 있어야 합니다.
- README, docs, guide, tests가 함께 갱신되어야 합니다.
- generated 결과 확인 경로가 끊기면 릴리즈하지 않습니다.
- breaking change는 문서에 명확히 남깁니다.

## 6. 품질 게이트

최소한 아래가 유지되어야 합니다.

- `python specyn.py validate --spec-dir specs/001-sample-service`
- `python specyn.py compile-prompts --spec-dir specs/001-sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service`
- `python specyn.py run --spec-dir specs/001-sample-service --project-id sample-service --workspace .workspace/sample-service`
- `pytest -q`
- 문서 링크와 quickstart 흐름 점검

## 7. 커뮤니티 운영 원칙

- 질문은 최대한 환영하는 방향으로 응답합니다.
- 버그는 재현 가능한 정보 중심으로 다룹니다.
- 기능 제안은 use case와 spec impact를 같이 봅니다.
- 표준화를 이야기할수록 governance와 compatibility를 더 엄격히 봅니다.

## 8. 앞으로 강화할 항목

- maintainer 역할 공개
- release cadence / changelog 정책 정립
- benchmark와 compatibility matrix 운영
- community sample catalog 운영
- label / triage 정책 고도화
