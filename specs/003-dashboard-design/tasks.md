---
id: dashboard-design-test
type: test
version: 1.0.0
owner_agent: test
status: draft
depends_on: [api, product]
---

# 목적
Design.md 변경이 현재 dashboard 구현과 어긋나지 않는지 검증할 테스트 기준을 정의한다.

# 입력
## 시나리오
- App.tsx에 정의된 route가 Design.md의 route 목록과 일치한다.
- AppShell sidebar link 목록이 Design.md의 공통 레이아웃 설명과 일치한다.
- DashboardPage가 health metric, runtime map, execution order, run history를 유지한다.
- WorkspacePage가 SpecBundleEditor, RunControls, ResultTimeline을 유지한다.
- planned 기능은 disabled button 또는 planned badge로 표현된다.

# 출력
- 디자인 스펙 정합성 테스트 기준
- route, layout, page component 확인 목록
- planned 상태 검증 기준

# 실행 규칙
1. Design.md 변경 전 테스트 기대값을 먼저 갱신한다.
2. 구현 변경은 실패하는 테스트를 확인한 뒤 진행한다.
3. 스냅샷보다 route, label, state contract 중심으로 검증한다.
4. 구현되지 않은 기능의 동작 테스트를 만들지 않는다.

# Validation 기준
- 테스트 시나리오는 4개 이상이어야 한다.
- route와 component mapping 검증이 포함되어야 한다.
- planned 상태 검증이 포함되어야 한다.

# Prompt
## Role
당신은 Test Agent로서 Design.md와 dashboard 구현의 정합성 테스트를 설계한다.

## Instructions
1. 현재 구현된 컴포넌트를 기준으로 테스트 대상을 고른다.
2. 새 기능은 테스트 실패를 먼저 만든 뒤 구현한다.
3. planned 상태는 실제 기능처럼 검증하지 않는다.

## Format
1. test scope
2. scenarios
3. acceptance criteria
4. remaining gaps
