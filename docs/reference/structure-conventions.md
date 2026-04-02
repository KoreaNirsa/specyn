# Structure Conventions

이 문서는 생성 대상 애플리케이션 구조를 빠르게 참고하기 위한 요약본입니다. 현재 기준 설명은 [아키텍처 개요](../architecture.md)와 함께 읽는 편이 좋습니다.

## Spring Boot

```text
com.example.sample
└── global
└── common
└── domain
```

| 구역 | 책임 |
|---|---|
| `global` | 설정, 예외 처리, 보안, 로깅 같은 전역 관심사 |
| `common` | 여러 도메인에서 재사용하는 공통 구성 요소 |
| `domain` | 실제 비즈니스 기능과 bounded context |

## FastAPI / LangChain

```text
app
└── global
└── common
└── domain
```

| 구역 | 책임 |
|---|---|
| `app/global` | 설정, 예외 핸들러, 미들웨어, 로깅 |
| `app/common` | 공통 schema, dependency, util |
| `app/domain` | 실제 비즈니스 기능 |
