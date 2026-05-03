# agents

Specyn의 Agent 정의는 코드와 분리된 Markdown 문서로 관리한다.

## 목적
- 역할 분리
- handoff 규칙 고정
- validation ownership 명확화
- 프롬프트 품질 일관성 확보
- 프로젝트 특성에 따라 실행 그래프를 조합할 수 있는 AX Builder 기반 제공

## 기본 Agent 카탈로그
### 기획 / 설계
- planner-agent
- design-agent
- orchestrator-agent
- rag-agent

### 구현
- api-agent
- backend-agent
- frontend-agent
- dba-agent
- devops-agent

### 검증 / 품질
- test-agent
- code-analysis-agent
- security-agent
- performance-agent
- review-agent
- final-review-agent
- docs-agent

## 원칙
- spec bundle을 source of truth로 사용
- 특정 예제 도메인보다 재사용 가능한 설계/명명 규칙을 우선
- 다음 agent가 바로 사용할 수 있는 산출물 중심으로 작성
- TODO 대신 가정(`ASSUMPTION:`)과 리스크(`RISK:`)를 명시
- validation 기준과 stop 조건을 각 agent 문서에 포함
- `plan.md`의 `execution_flow`가 기본 실행 순서를 결정
- `plan.md`의 `feedback_loops`와 `max_feedback_rounds`가 bounded 반복 협업을 결정
- 동일 Agent 재실행 시에는 feedback round 원칙을 따른다
- 가능하면 `STEP_LABEL / PHASE / FEEDBACK_ROUND / STATUS / CHANGED_FILES / NEXT_HANDOFF` trace metadata를 남긴다
