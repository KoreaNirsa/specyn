---
id: dashboard-design-review
type: review
version: 1.0.0
owner_agent: review
status: draft
depends_on: [product, api, test]
---

# 목적
Design.md와 dashboard 구현 변경의 리뷰 기준을 정의한다.

# 입력
## 구조 규칙
- route, page, component 책임이 Design.md와 일치해야 한다.
- AppShell 공통 레이아웃 변경은 모든 page 영향 범위를 명시해야 한다.

## 보안 규칙
- 외부 링크는 새 창 정책과 rel 속성을 유지해야 한다.
- 오류 메시지는 secret 또는 local credential을 노출하지 않아야 한다.

## 테스트 규칙
- Design.md 변경은 route/layout/page state 테스트와 함께 검토한다.
- planned 기능을 활성 기능처럼 테스트하거나 문서화하지 않는다.

## 운영 규칙
- dashboard와 sample runtime port 표시는 현재 실행 문서와 일치해야 한다.
- health down 상태는 사용자가 원인을 추적할 수 있어야 한다.

# 출력
- Design.md 리뷰 체크리스트
- blocker, major, minor 판단 기준
- 미구현 기능 처리 기준

# 실행 규칙
1. 스펙에 없는 UI 변경은 blocker로 본다.
2. 구현된 화면과 Design.md가 다르면 major로 본다.
3. planned 기능을 completed로 표현하면 blocker로 본다.
4. 단순 문구 보정은 기능 계약을 바꾸지 않는 범위에서만 허용한다.

# Validation 기준
- review 체크리스트는 4개 이상이어야 한다.
- 구조, 보안, 테스트, 운영 규칙을 모두 포함해야 한다.
- blocker 기준이 명시되어야 한다.

# Prompt
## Role
당신은 Review Agent로서 Design.md와 dashboard 구현의 불일치를 찾는다.

## Instructions
1. 스펙과 구현의 차이를 severity로 분류한다.
2. planned와 implemented 상태를 엄격히 구분한다.
3. 스펙에 없는 변경은 승인하지 않는다.

## Format
1. findings
2. severity
3. required fixes
4. residual risk
