---
id: sample-service-product
type: product
version: 1.3.0
owner_agent: planner
status: draft
depends_on: []
---

# 목적
sample-service를 spec 기반으로 생성하고 실행까지 확인할 수 있는 reference CRUD project 요구사항을 정의한다.

# 입력
## 배경
- dashboard에서 spec bundle을 편집하고 agent를 실행하면 sample-service code가 생성되어야 한다.
- 생성된 sample-service는 frontend, backend, ai-server를 포함한 runnable project여야 한다.

## 핵심 시나리오
1. 사용자가 task를 생성한다.
2. 사용자가 task 목록과 detail을 확인한다.
3. 사용자가 task status를 PENDING 또는 DONE으로 변경한다.
4. 사용자가 task를 삭제한다.
5. 사용자가 generated runtime을 직접 실행하고 동작을 확인한다.

## 비기능 요구사항
- dashboard와 sample-service의 역할이 분리되어야 한다.
- sample-service runtime은 local 환경에서 바로 실행 가능해야 한다.
- validation 오류는 사람이 읽을 수 있는 메시지로 보여야 한다.

# 출력
- sample-service가 만족해야 하는 product 요구사항
- downstream spec이 재사용할 용어와 acceptance criteria

# 실행 규칙
1. sample-service는 완성된 template가 아니라 agent 산출물이다.
2. generated code는 projects/sample-service 아래에 기록한다.
3. generated runtime에서 CRUD 흐름이 끝까지 동작해야 한다.

# Validation 기준
- 핵심 시나리오가 3개 이상 있어야 한다.
- 비기능 요구사항이 포함되어야 한다.
- output과 execution rule이 명확해야 한다.

# Prompt
## Role
당신은 Planner Agent다. sample-service를 reference sample로 정의한다.

## Instructions
1. product 요구사항과 acceptance criteria를 정리한다.
2. downstream agent가 사용할 용어를 고정한다.
3. runtime 확인 포인트를 포함한다.

## Format
1. 작업 요약
2. 도메인 용어
3. acceptance criteria
4. runtime 확인 포인트
