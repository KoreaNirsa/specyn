---
id: grill-me-product
type: product
version: 1.0.0
owner_agent: planner
status: draft
depends_on: []
---

# 목적
Grill Me 기법을 Specyn 스펙 리뷰 절차에 도입해 불명확한 요구사항을 구현 전에 드러낸다.

# 입력
## 핵심 시나리오
- 작성자는 새 feature 스펙을 구현 전에 Grill Me 질문으로 검증한다.
- 리뷰어는 스펙의 모호한 입력, 출력, 예외, 검증 기준을 질문으로 압박한다.
- 구현자는 답변되지 않은 항목을 추측하지 않고 TODO 또는 blocker로 남긴다.
- final-review는 Grill Me 미해결 질문이 남아 있으면 승인하지 않는다.

## 비기능 요구사항
- 질문은 스펙의 목적, 입력, 출력, 실행 규칙, Validation 기준에 연결되어야 한다.
- 질문은 공격적 표현이 아니라 요구사항 검증 목적이어야 한다.
- 답변 없는 질문은 구현 범위에 포함하지 않는다.
- Grill Me 결과는 review 또는 plan handoff에 남겨 추적 가능해야 한다.

## 제외 범위
- 코드 자동 수정
- 사람을 평가하는 인사/성과 절차
- 스펙과 무관한 일반 토론
- 답변 없는 요구사항의 임의 구현

# 출력
- Grill Me 질문 목록
- 답변된 결정 사항
- 미해결 blocker 또는 TODO
- 구현 전 스펙 보완 요청

# 실행 규칙
1. Grill Me는 구현 전 review 단계에서 수행한다.
2. 질문은 반드시 스펙 문서의 특정 섹션에 연결한다.
3. 답변이 없으면 구현하지 않는다.
4. 반복 질문은 최대 2회로 제한하고 이후 blocker로 전환한다.

# Validation 기준
- 핵심 시나리오는 3개 이상이어야 한다.
- 비기능 요구사항은 4개 이상이어야 한다.
- 제외 범위가 비어 있으면 안 된다.
- 질문 결과는 resolved와 unresolved로 분리되어야 한다.

# Prompt
## Role
당신은 Planner Agent로서 Grill Me 리뷰 절차의 목적과 범위를 정의한다.

## Instructions
1. 요구사항을 구현 가능한 수준으로 검증한다.
2. 추측이 필요한 지점은 질문으로 남긴다.
3. 답변 없는 항목은 구현하지 않는다는 원칙을 고정한다.

## Format
1. review goal
2. question set
3. resolved decisions
4. unresolved blockers
