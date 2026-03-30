# 04. Codex Execution

Specyn은 Codex를 **코드 생성/수정 실행기**로 사용한다.

## 실행 방식

### CLI 모드

- 로컬 workspace에 직접 코드 생성
- `CODEX_COMMAND_TEMPLATE` 환경 변수로 실행 명령 제어
- prompt를 표준 입력으로 주입

예시:

```bash
codex exec --json --cwd .workspace/todo-service
```

### API/Proxy 확장 모드

현재 템플릿은 CLI 모드를 기본 구현으로 제공한다.
조직 환경에서는 별도 게이트웨이/프록시로 확장할 수 있다.

## 파일 생성 방식

1. spec → prompt 변환
2. Codex 실행
3. 신규 파일 생성 또는 unified diff patch 반환
4. Test Agent / Review Agent가 후속 검증
5. 실패 시 patch 방향 또는 재수정 수행

## 운영 권장 사항

- workspace를 프로젝트별로 격리한다.
- prompt snapshot과 실행 로그를 보관한다.
- branch-per-run 또는 ephemeral runner로 확장 가능하도록 설계한다.
