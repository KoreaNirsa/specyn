# 🌟 커뮤니티 성장 가이드

이 문서는 Specyn이 더 많은 사용자와 star를 얻기 위해 어떤 신호를 강화해야 하는지 정리합니다.

## 1. 지금 저장소 안에서 이미 강화한 것

- **가치 제안이 보이는 README**
- **sample-flow 기반의 빠른 성공 경로**
- **실행 가능한 CRUD reference sample**
- **why/comparison 문서**
- **issue/PR/support/governance 문서**
- **multi-OS CLI smoke workflow**
- **Dependabot 설정과 Copilot repository instructions**

즉, “처음 방문한 사람이 무엇인지 이해하고, 바로 실행해 보고, 기여 경로를 찾는 것”을 우선 강화했습니다.

## 2. star를 늘리는 핵심 지표

정량 지표가 완벽하지 않아도 아래를 지속적으로 보면 좋습니다.

| 지표 | 의미 |
|---|---|
| Time to first success | bootstrap 후 sample-service를 띄우기까지 걸리는 시간 |
| Quickstart completion | 문서만 보고 끝까지 도달하는 사용자 비율 |
| Sample reuse | sample-service를 참고해 새 spec를 만든 사례 수 |
| Community response time | 질문/이슈/PR 첫 응답 속도 |
| External references | 블로그, 영상, 발표, 사내 도입 사례 |

## 3. 공개 직후 가장 중요한 운영 습관

1. 첫 주에는 이슈/질문 응답 속도를 높입니다.
2. README와 quickstart를 자주 다듬습니다.
3. sample-service를 깨뜨리는 변경을 매우 엄격히 막습니다.
4. 작은 성공 사례를 빠르게 문서화합니다.
5. 릴리즈 노트를 짧더라도 꾸준히 남깁니다.

## 4. Specyn이 “SDD 표준”으로 가기 위해 필요한 축

### 이해 가능성

- 처음 보는 사람이 3분 안에 핵심 가치를 이해할 수 있어야 합니다.
- 왜 필요한지, 다른 접근과 무엇이 다른지 바로 보여야 합니다.

### 재현 가능성

- sample-flow, CI, reference sample이 항상 살아 있어야 합니다.
- 문서, generated artifacts, 테스트가 함께 검증되어야 합니다.

### 확장 가능성

- agent 추가, runtime 교체, sample 확장이 쉬워야 합니다.
- 외부 통합(Codex, Copilot, 사내 agent) 포인트가 분명해야 합니다.

### 신뢰 가능성

- 보안/거버넌스/릴리즈/지원 경로가 보여야 합니다.
- placeholder, 죽은 링크, 오래된 문서가 없어야 합니다.

## 5. 메인테이너가 직접 해야 하는 공개 후 액션

아래는 저장소 파일만으로는 끝나지 않는 운영 액션입니다.

- GitHub Discussions 활성화
- 저장소 description/topics/social preview 정비
- 릴리즈 생성과 changelog 축적
- benchmark / 데모 영상 공개
- adoption 사례 수집
- label triage 정책 운영
- maintainer GitHub handle 기반 CODEOWNERS 확정

이 항목들은 저장소 밖 운영과 연결되므로 [../GOVERNANCE.md](../GOVERNANCE.md), [roadmap.md](roadmap.md) 와 함께 관리하는 편이 좋습니다.
