# Specyn

Specyn은 spec bundle, agent 실행, 생성 산출물, 로컬 런타임 검증, 대시보드를 하나의 흐름으로 묶는 Spec Driven Development 워크스페이스입니다.

현재 기준 진입점은 `python specyn.py ...` 입니다. `scripts/specyn_tasks.py`는 로컬 호스트 기반 보조 실행용 헬퍼이며, 기본 사용 경로는 아닙니다.

## 핵심 흐름

1. `python specyn.py setup`
2. `python specyn.py auth-status`
3. `python specyn.py doctor`
4. `python specyn.py up -d`
5. 대시보드 `Workspace` 페이지에서 agent 실행
6. 필요하면 `python specyn.py sample-up -d` 로 sample-service 런타임 확인

Spec 위치:

- `specs/templates/`: 새 프로젝트를 시작할 때 복사해서 쓰는 템플릿
- `specs/projects/sample-service/`: `validate`, `compile-prompts`, `run` 기준 reference sample

## 사전 준비

최초 실행 전 아래 도구가 필요합니다.

- Docker Desktop
- Python 3.11+
- Node.js 20+ 및 npm

권장 확인:

```bash
python --version
node --version
npm --version
docker version
```

## 빠른 시작

레포 루트에서 실행합니다.

```bash
python specyn.py setup
python specyn.py auth-status
python specyn.py doctor
python specyn.py up -d
```

대시보드 주소:

- Frontend: `http://localhost:4173`
- Backend: `http://localhost:8180`
- AI Server: `http://localhost:8100`

sample-service 생성물까지 실제 런타임으로 확인하려면:

```bash
python specyn.py sample-up -d
```

sample-service 주소:

- Frontend: `http://localhost:5173`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI context: `http://localhost:8000/generated/sample-service/context`

중지:

```bash
python specyn.py down
python specyn.py sample-down
```

## setup 이 하는 일

`python specyn.py setup` 은 다음 항목을 다룹니다.

- `.env` 생성 또는 갱신
- 인증 방식 선택: `chatgpt` 또는 `openapi`
- ChatGPT 로그인 재사용 또는 재로그인
- `OPENAI_API_KEY` 입력 또는 갱신
- 실행 모델 선택
- Docker 사용 가능 시 agent 실행 준비 상태 점검

## 수동 CLI 흐름

대시보드 없이 spec 기준 흐름만 직접 실행할 수도 있습니다.

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
```

보조 호스트 실행 모드가 필요할 때만 아래 헬퍼를 사용합니다.

```bash
python scripts/specyn_tasks.py dev
python scripts/specyn_tasks.py sample-dev
```

## 주요 로컬 경로

- `.env`: 로컬 실행 설정
- `.specyn/codex`: 로컬 인증 및 캐시
- `.workspace/`: 로컬 실행 산출물과 trace
- `projects/sample-service/`: 생성된 sample-service 결과물

## 주의 사항

- `.env` 는 커밋하지 않습니다.
- `.specyn/codex` 는 공유하지 않습니다.
- `.workspace/` 는 로컬 산출물로 취급합니다.
- Docker Desktop 이 꺼져 있으면 `setup` 은 일부만 완료되고 실제 스택 기동은 실패할 수 있습니다.
- 대시보드에서 agent 실행 버튼은 `Dashboard` 가 아니라 `Workspace` 페이지에 있습니다.

## 문서 안내

- [문서 인덱스](docs/README.md)
- [빠른 시작](docs/quickstart.md)
- [운영 가이드](docs/operations.md)
- [CLI 실행 참고](docs/cli-run-reference.md)
- [샘플 서비스 참고](docs/sample-service-reference.md)
- [트러블슈팅](docs/troubleshooting.md)
- [로컬 개발](guide/local-development.md)
