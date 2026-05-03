---
id: dashboard-design-design
type: design
version: 1.0.0
owner_agent: design
status: draft
depends_on: [product]
---

# 목적
현재 구현된 dashboard frontend 기준으로 화면 구조, 상태 표현, 사용자 흐름을 고정한다.

# 입력
## 구현된 route
- `/`: DashboardPage
- `/workspace`: WorkspacePage
- `/runs`: RunsPage
- `/agents`: AgentsPage
- `/ci-deploy`: DeploymentsPage
- `/system`: SystemPage
- `/projects`: ProjectsPage

## 공통 레이아웃
- AppShell은 sidebar, topbar, page-body, footer를 제공한다.
- sidebar는 Dashboard, Workspace, Runs, Agents, Deploy, System, Projects 링크를 제공한다.
- sidebar footer는 dashboard와 sample runtime port를 service pill로 표시한다.
- topbar는 언어 선택과 agent console 진입 버튼을 제공한다.

## 화면별 정보 구조
- DashboardPage는 health metric, spec bundle size, output project, runtime map, execution order, run history를 표시한다.
- WorkspacePage는 health metric, SpecBundleEditor, RunControls, ResultTimeline을 표시한다.
- RunsPage는 RunHistoryTable, ResultTimeline, logs, prompt preview, generated files placeholder를 표시한다.
- AgentsPage는 planner, backend/frontend, review/docs agent 카드와 planned badge를 표시한다.
- ProjectsPage는 sample-service와 future-project-template runtime 상태를 표시한다.

## 상태 표현
- StatusBadge tone은 success, warning, danger를 사용한다.
- health 실패는 danger, 실행 중은 warning, 정상/active는 success로 표현한다.
- 아직 구현되지 않은 기능은 planned badge나 disabled button으로만 표시한다.

# 출력
- dashboard 화면 설계 기준
- 화면별 정보 구조
- 상태 표현 기준
- future work에서 유지해야 할 UI 계약

# 실행 규칙
1. Design.md는 구현된 dashboard 화면을 설명하는 기준 문서다.
2. 새 화면을 추가하려면 먼저 이 문서에 route, 정보 구조, 상태 표현을 추가한다.
3. planned 상태는 실제 동작으로 간주하지 않는다.
4. sample-service runtime 링크와 dashboard runtime port 표시는 현재 계약을 유지한다.

# Validation 기준
- route 목록이 App.tsx의 route와 일치해야 한다.
- Design.md는 Dashboard, Workspace, Runs, Agents, Projects의 현재 구현 정보를 포함해야 한다.
- planned 기능은 명시적으로 planned 또는 disabled로 표시되어야 한다.
- 상태 표현 기준이 StatusBadge tone과 충돌하지 않아야 한다.

# Prompt
## Role
당신은 Design Agent로서 dashboard UI의 현재 구현 기준을 스펙으로 고정한다.

## Instructions
1. App.tsx, AppShell, page component에서 확인한 사실만 작성한다.
2. 화면별 책임과 상태 표현을 분리한다.
3. 향후 UI 변경은 이 문서를 먼저 갱신한 뒤 진행한다.

## Format
1. route map
2. layout contract
3. page information architecture
4. state and interaction rules
