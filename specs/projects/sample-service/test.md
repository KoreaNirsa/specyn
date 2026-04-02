---
id: sample-service-test
type: test
version: 1.4.0
owner_agent: test
status: draft
depends_on: [api]
---

# 목적
sample-service CRUD runtime이 contract대로 동작하는지 검증하는 test 시나리오를 정의한다.

# 입력
## 검증 대상
- backend API
- generated frontend flow
- ai-server health 및 generated context
- sample-up 포트 계약: frontend `3000`, backend `8080`, ai-server `8000`
- frontend React runtime 계약: `React is not defined`가 없어야 함

## 전달 테스트
1. task 생성 성공
2. task 목록 조회 성공
3. task detail 조회 성공
4. status 변경 성공과 validation 실패
5. 삭제 성공 및 재조회 404

# 출력
- automated test 기준
- manual smoke test 체크리스트
- runtime 확인 evidence 사인

# 실행 규칙
1. success와 failure case를 모두 포함한다.
2. CRUD 전체 흐름을 검증한다.
3. runtime 확인 절차를 문서화한다.
4. frontend manual smoke는 `http://localhost:3000` 기준으로 검증한다.
5. frontend smoke는 첫 화면 로드 시 console/runtime exception 없이 렌더링되어야 한다.

# Validation 기준
- 400, 404, 204 케이스가 포함되어 있어야 한다.
- frontend manual smoke가 포함되어 있어야 한다.
- generated runtime 확인 evidence가 있어야 한다.
- 포트 계약 불일치를 blocker 또는 major로 드러낼 수 있어야 한다.
- `React is not defined` 같은 frontend bootstrap 오류를 잡을 수 있어야 한다.

# Prompt
## Role
당신은 Test Agent다. sample-service runtime 검증 시나리오를 만든다.

## Instructions
1. CRUD 전체 흐름을 다룬다.
2. validation과 not-found 케이스를 포함한다.
3. manual smoke test를 함께 정리한다.
4. `sample-up` 기준 frontend 확인 URL을 `http://localhost:3000`으로 고정한다.
5. frontend bootstrap 실패(`React is not defined`, import 누락, JSX runtime mismatch)를 명시적으로 검증한다.

## Format
1. 작업 요약
2. test 목록
3. coverage 체크사인
4. runtime 확인 evidence
