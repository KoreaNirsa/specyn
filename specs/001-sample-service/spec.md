---
id: sample-service-product
type: product
version: 1.4.2
owner_agent: planner
status: draft
depends_on: []
---

# 목적
sample-service를 spec 기반으로 생성하고 실행까지 검증할 수 있는 reference CRUD 프로젝트 요구사항을 정의한다.

# 입력
## 비즈니스 배경
- dashboard에서 spec bundle을 편집하고 agent를 실행하면 sample-service 코드가 생성되어야 한다.
- 생성 결과물은 frontend, backend, ai-server를 포함한 runnable project여야 한다.

## 문제 정의
- 샘플 프로젝트가 없으면 spec 변경이 실제 생성물에 어떤 영향을 주는지 검증하기 어렵다.
- 문서, 코드, 실행 방법 사이의 drift가 생기면 PR 단계에서 품질을 보장할 수 없다.

## 핵심 사용자
- Specyn maintainer
- dashboard를 통해 생성 흐름을 검증하는 개발자

## 핵심 시나리오
- 사용자가 새 task를 생성한다.
- 사용자가 task 목록과 상세 정보를 조회한다.
- 사용자가 task 상태를 `PENDING`에서 `DONE`으로 변경한다.
- 사용자가 task를 삭제하고 삭제 후 404 동작을 확인한다.
- 사용자가 generated runtime을 직접 실행해 frontend, backend, ai-server 연결 상태를 확인한다.

## 비기능 요구사항
- 보안: 로컬 샘플 서비스는 인증 없이 실행 가능하되 오류 응답 구조는 일관돼야 한다.
- 성능: 일반 CRUD 요청은 로컬 개발 환경에서 체감 지연 없이 처리되어야 한다.
- 운영: `sample-up` 실행 기준 포트 계약은 frontend `5173`, backend `8080`, ai-server `8000` 이어야 한다.
- UX: generated frontend는 브라우저 초기 로드 시 `React is not defined` 같은 bootstrap 오류가 없어야 한다.
- 문서: generated docs와 runbook은 실제 실행 포트와 동일해야 한다.

## 제외 범위
- 사용자 인증/인가 기능
- 파일 업로드
- 다중 프로젝트 관리
- 운영 배포용 인프라 구성

# 출력
- sample-service가 만족해야 하는 product 요구사항
- downstream spec이 재사용할 acceptance criteria

# 실행 규칙
1. generated code는 `projects/sample-service` 아래에 기록한다.
2. generated runtime에서 CRUD 흐름이 실제로 동작해야 한다.
3. `sample-up` 포트 계약은 spec, docs, compose 결과와 동일해야 한다.
4. frontend source와 build 결과물은 JSX runtime 계약과 일치해야 한다.

# Validation 기준
- 핵심 시나리오는 3개 이상이어야 한다.
- 비기능 요구사항은 충분히 구체적이어야 한다.
- 제외 범위가 비어 있지 않아야 한다.

# Prompt
## Role
당신은 Planner Agent로서 sample-service를 reference sample로 정의한다.

## Instructions
1. product 요구사항과 acceptance criteria를 정리한다.
2. downstream agent가 재사용할 용어를 고정한다.
3. runtime 확인 포인트와 포트 계약을 명확히 적는다.

## Format
1. 작업 요약
2. 도메인 용어
3. acceptance criteria
4. runtime 확인 사항
