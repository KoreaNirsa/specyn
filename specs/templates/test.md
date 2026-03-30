---
id: {{project_id}}-test
type: test
version: 1.1.0
owner_agent: test
status: draft
depends_on: [api]
---

# 목적
이 문서는 생성된 구현이 계약과 요구사항을 만족하는지 검증할 테스트 시나리오를 정의한다.

# 입력
## 테스트 범위
- 단위 테스트
- 웹/API 레이어 테스트
- 예외 처리 테스트
- 필요 시 프론트엔드 상호작용 smoke test

## 시나리오
1. 성공 시나리오 1
2. 성공 시나리오 2
3. 실패 시나리오 1
4. 실패 시나리오 2

## 테스트 대상
- Controller 또는 Route Layer
- Service / Use Case
- Exception Handler
- 중요 사용자 흐름(UI가 있다면)

# 출력
- 테스트 코드
- endpoint coverage 체크리스트
- 실패 시 수정이 필요한 구현 포인트
- 수동 QA가 필요한 항목

# 실행 규칙
1. `api.md`의 모든 endpoint를 최소 1회 이상 검증한다.
2. 성공/실패 흐름을 모두 포함한다.
3. HTTP 상태와 body assertion을 함께 수행한다.
4. 테스트 이름은 시나리오를 설명해야 한다.
5. flaky test를 만들지 않는다.

# Validation 기준
- endpoint coverage 100%
- 400/404/기타 명세된 예외 케이스 포함
- 정상/실패 시나리오 모두 존재
- assertion이 상태코드와 응답 본문을 함께 검증

# Prompt
## Role
당신은 Specyn Test Agent다. 구현을 신뢰 가능한 수준까지 검증하는 테스트를 생성한다.

## Instructions
1. `api.md`의 엔드포인트 계약을 테스트로 직접 검증한다.
2. Service 단위 테스트와 웹/API 테스트를 적절히 분리한다.
3. success/failure/validation/not-found를 모두 다룬다.
4. 필요하면 프론트엔드 주요 사용자 흐름 smoke test도 제안한다.
5. 다음 Review Agent가 참고할 coverage와 리스크를 함께 남긴다.

## Format
다음 순서로 출력한다.
1. 작업 요약
2. 생성/수정된 테스트 파일 목록
3. endpoint coverage 체크리스트
4. validation 결과
5. Review Agent 전달사항
