---
id: dashboard-design-product
type: product
version: 1.0.0
owner_agent: design
status: draft
depends_on: []
---

# 목적
현재 구현된 Specyn dashboard 화면을 기준으로 유지보수 가능한 Design.md 기준을 정의한다.

# 입력
## 핵심 시나리오
- 사용자는 Dashboard에서 backend, AI server, sample runtime 상태와 실행 이력을 확인한다.
- 사용자는 Workspace에서 spec bundle을 편집하고 sample-service agent run을 시작한다.
- 사용자는 Runs에서 run history, timeline, 로그, prompt preview, generated files 영역을 확인한다.
- 사용자는 Projects에서 sample-service와 future project template 상태를 비교한다.

## 비기능 요구사항
- 현재 구현된 route와 컴포넌트 이름을 기준으로 화면 계약을 설명한다.
- 구현되지 않은 화면 동작은 planned 상태로만 표기한다.
- dashboard frontend, backend, AI server, sample-service runtime port 계약을 유지한다.
- 한 화면에서 상태, 실행, 산출물 확인 흐름이 끊기지 않아야 한다.

## 제외 범위
- 새로운 UI 기능 구현
- 신규 API 추가
- 대시보드 인증/권한 설계
- 디자인 시스템 전면 재작성

# 출력
- 현재 dashboard 기준 Design.md 스펙
- 화면별 정보 구조와 상태 표현 기준
- 향후 디자인 변경 시 확인할 검증 기준

# 실행 규칙
1. 스펙은 현재 구현된 dashboard route와 컴포넌트를 기준으로 작성한다.
2. 구현되지 않은 기능은 planned 또는 TODO로만 남긴다.
3. 화면 문구나 레이아웃을 임의로 변경하지 않는다.
4. Design.md는 feature bundle의 보조 스펙이며 구현 변경의 선행 기준으로 사용한다.

# Validation 기준
- 핵심 시나리오는 3개 이상이어야 한다.
- 비기능 요구사항은 4개 이상이어야 한다.
- 제외 범위가 명시되어야 한다.
- Design.md가 현재 구현된 dashboard 화면 경로를 포함해야 한다.

# Prompt
## Role
당신은 Design Agent로서 현재 구현된 dashboard 화면을 기준으로 디자인 스펙을 정리한다.

## Instructions
1. 코드에 존재하는 route와 컴포넌트만 근거로 삼는다.
2. 구현되지 않은 동작은 구현된 것처럼 쓰지 않는다.
3. 디자인 기준은 다음 구현 작업의 입력으로 사용할 수 있게 구체화한다.

## Format
1. 화면 목록
2. 화면별 정보 구조
3. 상태와 인터랙션
4. 검증 기준
