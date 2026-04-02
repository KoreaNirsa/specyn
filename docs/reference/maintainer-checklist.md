# Maintainer Checklist

릴리즈나 주요 구조 변경 전에는 아래 항목을 함께 보는 편이 좋습니다.

## 릴리즈 전 체크 흐름

```text
spec/template change
  -> example spec sync
  -> agent docs sync
  -> validator/test sync
  -> README/docs sync
  -> cross-platform command check
  -> zip/package sanity check
```

## 체크리스트

- `specs/templates`를 바꿨다면 `specs/projects/sample-service`도 같이 갱신했는가
- Prompt 계약을 바꿨다면 Agent 문서와 Prompt Builder가 함께 반영되었는가
- `bootstrap -> doctor -> validate-spec -> compile-prompts -> run-sim` 경로가 유지되는가
- Windows / Linux / macOS 문서가 함께 맞는가
- README와 docs 링크가 깨지지 않는가
- feedback loop 추가로 prompt 파일명이 충돌하지 않는가
