# 10. Structure Conventions

Specyn은 특정 도메인에 종속되지 않는 AX Builder 프레임워크이므로,
생성 대상 애플리케이션의 기본 구조도 **도메인 중립적이고 확장 가능한 규약**을 우선한다.

## 1. Spring Boot 기본 규약

Spring Boot 서비스는 `global / common / domain` 3축 구조를 권장한다.

```text
com.example.sample
├── global
│   ├── config
│   ├── error
│   ├── logging
│   ├── response
│   └── security
├── common
│   ├── annotation
│   ├── constant
│   ├── util
│   └── model
└── domain
    └── order
        ├── api
        ├── application
        │   ├── service
        │   └── port
        ├── domain
        │   ├── model
        │   └── policy
        └── infrastructure
            ├── client
            └── persistence
```

### 역할 정리

| 구역 | 책임 |
|---|---|
| global | 예외 처리, 공통 응답, 설정, 보안, 로깅 등 횡단 관심사 |
| common | 여러 도메인에서 재사용 가능한 annotation/util/base model |
| domain | 실제 비즈니스 기능. bounded context 단위로 분리 |

### 설계 원칙
- Controller/Facade는 `domain.<context>.api`에 둔다.
- 유스케이스와 서비스는 `domain.<context>.application`에 둔다.
- 핵심 모델과 정책은 `domain.<context>.domain`에 둔다.
- JPA/Redis/외부 API 연동은 `domain.<context>.infrastructure`에 둔다.
- `global`과 `common`이 도메인 로직을 먹어버리지 않게 주의한다.

## 2. FastAPI / LangChain 기본 규약

FastAPI/LangChain 서비스도 같은 사고방식을 유지하되 Python 관례에 맞게 적용한다.

```text
app
├── global
│   ├── config.py
│   ├── exception_handlers.py
│   ├── logging.py
│   └── middleware.py
├── common
│   ├── dependencies
│   ├── schemas
│   └── utils
└── domain
    └── retrieval
        ├── api.py
        ├── application
        ├── domain
        └── infrastructure
```

### 역할 정리

| 구역 | 책임 |
|---|---|
| app/global | 설정, 예외 핸들러, 미들웨어, 로깅, 보안 의존성 |
| app/common | 공통 schema, dependency, util |
| app/domain | 실제 비즈니스/AI 기능. API, application, domain, infrastructure 분리 |

### LangChain 적용 시 팁
- Retriever, embedding, vector store adapter는 `infrastructure`에 둔다.
- 체인/워크플로 orchestration은 `application`에 둔다.
- 핵심 질의 모델/정책/도메인 규칙은 `domain`에 둔다.
- FastAPI route는 가급적 얇게 유지하고 application 계층을 호출한다.

## 3. 무엇을 강제하고 무엇을 강제하지 않는가

```text
Specyn generated application
  -> 위 구조 규약을 기본값으로 권장

Specyn framework runtime itself
  -> 기존 폴더 구조를 유지할 수 있음
  -> 호환성/실행 안정성을 해치지 않는 범위에서 점진적 개선
```

즉, **생성 대상 서비스 규약**과 **현재 프레임워크 런타임 구현체**를 구분해서 본다.
프레임워크 내부 코드는 호환성과 실행 안정성을 우선할 수 있다.

## 4. 리뷰 체크포인트

- `global`에 도메인 로직이 과도하게 몰리지 않았는가
- `common`이 잡다한 쓰레기통 패키지가 되지 않았는가
- `domain`이 bounded context 기준으로 분리되었는가
- application/domain/infrastructure 경계가 실제 코드에서 살아 있는가
- 테스트가 공통 예외/검증 경계와 도메인 유스케이스를 모두 다루는가
