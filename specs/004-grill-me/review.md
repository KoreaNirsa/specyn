---
id: grill-me-review
type: review
version: 1.0.0
owner_agent: review
status: draft
depends_on: [product, api, test]
---

# 목적
Grill Me 질문 품질과 미해결 항목 처리 기준을 정의한다.

# 입력
## 구조 규칙
- 질문은 하나의 스펙 섹션과 하나의 검증 목적을 가져야 한다.
- 질문 결과는 resolved와 unresolved로 분리되어야 한다.

## 보안 규칙
- secret, token, 개인 정보 입력을 요구하는 질문을 만들지 않는다.
- 민감한 운영 환경 정보를 답변으로 요구하지 않는다.

## 테스트 규칙
- unresolved blocker는 테스트 실패 또는 final-review blocker로 연결한다.
- 질문이 테스트로 검증 불가능하면 major로 표시한다.

## 운영 규칙
- 반복 질문은 최대 2회까지만 허용한다.
- 답변 없는 요구사항은 구현 범위에서 제외한다.

# 출력
- Grill Me 리뷰 기준
- blocker/major/minor 분류
- 미해결 질문 처리 결과

# 실행 규칙
1. 모호한 요구사항은 질문으로 전환한다.
2. 답변이 스펙에 반영되지 않으면 resolved로 보지 않는다.
3. unresolved blocker가 있으면 구현 승인을 하지 않는다.
4. Grill Me는 사람 공격이 아니라 스펙 검증 절차로만 수행한다.

# Validation 기준
- review 체크리스트는 4개 이상이어야 한다.
- 구조, 보안, 테스트, 운영 규칙을 모두 포함해야 한다.
- unresolved blocker 정책이 명시되어야 한다.

# Prompt
## Role
당신은 Review Agent로서 Grill Me 질문의 품질과 처리 결과를 검토한다.

## Instructions
1. 질문이 스펙 섹션과 연결되어 있는지 확인한다.
2. unresolved blocker가 구현에 섞이지 않게 한다.
3. 답변이 스펙에 반영되었는지 확인한다.

## Format
1. findings
2. severity
3. unresolved blockers
4. required spec updates
