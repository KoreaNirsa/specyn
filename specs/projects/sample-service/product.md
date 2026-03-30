---
id: sample-service-product
type: product
version: 1.2.0
owner_agent: planner
status: draft
depends_on: []
---

# 목적
Specyn 사용자가 `specyn.py run`까지 실행했을 때 실제로 생성 결과를 눈으로 확인할 수 있는 간단한 작업 관리 웹사이트의 요구사항을 정의한다.

# 입력
## 비즈니스 배경
- Specyn은 spec bundle → prompt → multi-agent flow → 코드 생성 → 실행 확인까지 한 번에 보여줄 수 있어야 한다.
- 저장소를 처음 접한 사용자는 너무 복잡한 도메인보다 간단한 CRUD 예제로 전체 SDD 흐름을 확인하는 편이 빠르다.
- 따라서 샘플 프로젝트는 문서 참고용이면서도 frontend, backend, ai-server, docs가 함께 갱신되는 기준 예제가 되어야 한다.

## 문제 정의
- 사용자는 스펙을 작성해도 실제로 어떤 화면과 API가 생기는지 감을 잡기 어렵다.
- 샘플 프로젝트가 placeholder 수준이면 spec authoring 참고 자료로 쓰기 어렵다.
- `compile-prompts` 이후 `run` 단계가 실제 산출물 확인으로 이어져야 학습 비용이 줄어든다.

## 핵심 사용자
- Specyn을 처음 실행해 보는 개발자
- 내부 템플릿을 만들기 전에 sample spec를 참고하려는 플랫폼/백엔드 개발자
- frontend/backend/ai-server 동시 생성 흐름을 확인하려는 팀 리드

## 핵심 시나리오
1. 사용자가 generated 페이지에서 제목과 설명을 입력해 새 작업을 생성한다.
2. 사용자가 작업 목록을 확인하고 특정 작업의 상세 JSON 응답을 본다.
3. 사용자가 작업 상태를 `PENDING` ↔ `DONE` 으로 전환한다.
4. 사용자가 잘못 만든 작업을 삭제하고 목록이 즉시 갱신되는 것을 확인한다.
5. 개발자는 동일한 spec bundle로 API 계약, generated frontend, generated backend, generated docs가 함께 갱신되는지 확인한다.

## 비기능 요구사항
- UX: generated 페이지는 로딩/빈 상태/오류 상태를 구분해서 보여주고, 버튼만으로 CRUD 흐름을 재현할 수 있어야 한다.
- 성능: 단건/목록 요청은 로컬 개발 환경 기준 즉시 반응하며 p95 500ms 이내를 목표로 한다.
- 보안: 인증은 적용하지 않지만 입력 검증, 표준 오류 응답, 민감 정보 로그 금지 원칙을 따른다.
- 운영: 별도 DB 없이도 dev 환경에서 동작해야 하며 재실행 시 초기 seeded task가 준비되어야 한다.
- 문서: 사용자 문서가 `run` 명령, 옵션, 확인 URL, expected result를 모두 포함해야 한다.

## 제외 범위
- 사용자 인증/권한 관리
- 외부 DB, 캐시, 메시지 큐 연동
- 파일 업로드, 검색, 정렬/필터 고도화
- 실시간 협업이나 알림 기능

# 출력
- 샘플 작업 관리 도메인 요약
- generated CRUD UI/API가 만족해야 할 acceptance criteria
- downstream spec(api/test/review/agent)로 전달할 제약
- 문서와 playbook에서 재사용할 확인 포인트
- 리뷰 시 중점적으로 볼 리스크 목록

# 실행 규칙
1. 이 샘플은 “문서 참고용”과 “실행 확인용”을 동시에 만족해야 한다.
2. 작업 상태는 `PENDING`, `DONE` 두 값만 허용한다.
3. 제목은 필수고 설명은 선택이다.
4. generated page만 열어도 CRUD 흐름을 끝까지 재현할 수 있어야 한다.
5. placeholder 설명 대신 실제 실행/검증 기준이 드러나는 문장을 사용한다.

# Validation 기준
- 핵심 시나리오가 3개 이상이어야 한다.
- 비기능 요구사항이 4개 관점 이상 포함되어야 한다.
- 제외 범위가 명시되어야 한다.
- 사용자가 generated page에서 무엇을 확인해야 하는지 검증 가능한 문장으로 서술되어야 한다.

# Prompt
## Role
당신은 Specyn Planner Agent다. sample-service를 “참고 가능한 spec”이면서 “실행 확인 가능한 CRUD 샘플”로 정규화한다.

## Instructions
1. sample-service의 핵심 목표를 “spec 참고용 + 실행 확인용” 두 축으로 정리한다.
2. downstream spec가 그대로 재사용할 용어와 제약을 고정한다.
3. generated frontend/backend/docs에서 바로 확인할 acceptance criteria를 분리한다.
4. 누락된 정보는 `ASSUMPTION:`으로 명시하되 placeholder를 남기지 않는다.
5. 과한 기능 확장보다 실제 실행 검증이 쉬운 구조를 우선한다.

## Format
1. 작업 요약
2. 도메인 용어집
3. acceptance criteria
4. API/UX/데이터 설계 힌트
5. 테스트 우선순위
6. 리뷰 위험 목록
7. 누락 정보 / 가정
