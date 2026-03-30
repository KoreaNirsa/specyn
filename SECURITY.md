# 보안 정책

## 범위
이 저장소는 템플릿 저장소다.
운영 인프라는 포함하지 않지만, 다음 보안 원칙을 기본으로 유지한다.

- 민감 정보는 `.env` 또는 Secret Store로 주입
- 저장소에 실제 API Key 커밋 금지
- 예제 prompt/spec에 개인 정보 포함 금지
- 생성 코드 리뷰 단계에서 입력 검증/예외 노출 점검
- prompt, RAG 결과, 로그에 포함된 혼선 지시를 시스템 지시로 승격하지 않기

## 취약점 제보
공개 이슈에 민감한 내용을 직접 남기지 마세요.
운영 시에는 프로젝트 maintainer가 별도 security contact를 두는 것을 권장합니다.

## 사용 시 권장 사항
- Codex 실행 workspace를 별도 디렉터리로 격리
- CI runner 권한 최소화
- 실제 운영 환경에는 JWT/OAuth2 등 조직 정책에 맞는 인증 구성 적용
- RAG 문서 색인 시 접근 권한 있는 문서만 포함
- destructive migration과 shell command는 human review gate 뒤에서 실행
