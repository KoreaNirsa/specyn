# 🌍 오픈소스 공개 준비 상태

이 문서는 Specyn을 GitHub 저장소에서 **SDD 오픈소스 프레임워크**로 운영하기 위해 현재 준비된 항목과 남은 항목을 정리합니다.

## 현재 준비된 것

- `sample-service` reference sample과 실행 절차
- `validate -> compile-prompts -> run -> dev` 문서화
- `sample-flow` 기반 빠른 온보딩 경로
- CLI / Codex 실행 경로 분리
- spec validator, local runtime, 문서 무결성 테스트
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, `GOVERNANCE.md`
- issue template, PR template, community growth guide
- Dependabot 설정, multi-OS CLI smoke workflow, Copilot repository instructions

## 공개 전에 계속 챙길 것

1. sample-service 외에 하나 이상의 도메인 샘플 추가
2. Codex 실행 경로의 더 강한 회귀 테스트 추가
3. generated frontend/backend 의 실제 통합 테스트 확대
4. 릴리즈 노트와 버전 정책 정립
5. maintainer triage / labeling / backlog 운영 규칙 정리
6. benchmark / 사례 / 데모 영상 축적

## 공개 가능한 수준 판단

현재 상태는 **로컬 실행과 샘플 CRUD 데모를 중심으로는 공개 가능한 수준**입니다.
다만, 대외적으로 “프레임워크”라고 소개할 때는 아래를 계속 강화하는 편이 좋습니다.

- 다양한 샘플 도메인
- 안정적인 CI/CD
- 보안 보고 채널
- 명확한 버전/호환성 정책
- 커뮤니티 운영 문서
- 공개 벤치마크와 adoption 사례
