---
id: sample-service-product
type: product
version: 1.4.0
owner_agent: planner
status: draft
depends_on: []
---

# 목적
sample-service를 spec 기반으로 생성하고 실행까지 검증할 수 있는 reference CRUD project 요구사항을 정의한다.

# 입력
## 배경
- dashboard에서 spec bundle을 편집하고 agent를 실행하면 sample-service code가 생성되어야 한다.
- 생성된 sample-service는 frontend, backend, ai-server를 포함한 runnable project여야 한다.

## 전달 시나리오
1. 사용자가 task를 생성한다.
2. 사용자가 task 목록과 detail을 확인한다.
3. 사용자가 task status를 `PENDING` 또는 `DONE`으로 변경한다.
4. 사용자가 task를 삭제한다.
5. 사용자가 generated runtime을 직접 실행하고 동작을 확인한다.

## 비기능 요구사항
- dashboard와 sample-service의 역할이 분리되어야 한다.
- sample-service runtime은 local 환경에서 바로 실행 가능해야 한다.
- validation 오류는 원인을 읽을 수 있는 메시지로 보여야 한다.
- `python specyn.py sample-up -d` 기준 런타임 포트 계약은 frontend `http://localhost:3000`, backend `http://localhost:8080`, ai-server `http://localhost:8000` 이어야 한다.
- Docker runtime frontend는 non-root nginx container `8080`을 사용하고 host에는 `3000`으로 노출해야 한다.
- generated frontend는 browser runtime에서 `React is not defined` 오류가 없어야 한다.
- frontend build 산출물이 `React.createElement(...)`를 사용하면 해당 모듈에 `import React from "react"` 또는 동등한 바인딩이 반드시 있어야 한다.
- frontend가 automatic JSX runtime을 사용할 경우 `React` 전역 식별자에 의존하지 않아야 한다.

# 출력
- sample-service가 만족해야 하는 product 요구사항
- downstream spec가 재사용할 수 있는 acceptance criteria

# 실행 규칙
1. sample-service는 완성된 template가 아니라 agent 산출물이다.
2. generated code는 `projects/sample-service` 아래에 기록된다.
3. generated runtime에서 CRUD 흐름이 끝까지 동작해야 한다.
4. `sample-up` 실행 기준 포트 계약은 spec과 generated docs, runbook, compose 파일에서 동일해야 한다.
5. frontend source, build 설정, 번들 결과는 동일한 JSX runtime 계약을 따라야 한다.

# Validation 기준
- 전달 시나리오가 3개 이상 있어야 한다.
- 비기능 요구사항이 포함되어야 한다.
- output과 execution rule이 명확해야 한다.
- 런타임 포트 계약이 명시되어 있어야 한다.
- frontend JSX runtime 계약이 명시되어 있어야 한다.

# Prompt
## Role
당신은 Planner Agent다. sample-service를 reference sample로 정의한다.

## Instructions
1. product 요구사항과 acceptance criteria를 정리한다.
2. downstream agent가 재사용할 용어를 고정한다.
3. runtime 확인 사인을 포함한다.
4. `sample-up` 기준 frontend host port가 `3000`임을 명확하게 유지한다.
5. frontend는 React runtime 계약이 깨져 브라우저에서 `React is not defined`가 발생하지 않도록 요구사항을 고정한다.

## Format
1. 작업 요약
2. 도메인 용어
3. acceptance criteria
4. runtime 확인 사인
