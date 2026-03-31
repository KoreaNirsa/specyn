# Specyn

Specyn은 spec bundle을 기반으로 prompt, agent flow, generated code, docs, 실행 확인까지 이어지는 Spec Driven Development 저장소입니다.

이 저장소는 **대시보드 런타임**과 **실제 생성 프로젝트 런타임**을 분리해 둔 구조를 사용합니다.

## 구조

```text
/dashboard
  /frontend   # Specyn 관리자 대시보드 React
  /backend    # Specyn 대시보드 Spring Boot
  /ai-server  # Specyn 대시보드 FastAPI
/projects
  /_template  # 새 프로젝트 템플릿 자리
  /sample-service
    /frontend
    /backend
    /ai-server
    /docs
/specs
  /templates
  /projects/sample-service
```

## 포트 정책

### Specyn Dashboard
- Frontend: `http://localhost:4173`
- Backend: `http://localhost:8180`
- AI Server: `http://localhost:8100`

### sample-service 실제 프로젝트 런타임
- Frontend: `http://localhost:5173`
- Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- AI Server context: `http://localhost:8000/generated/sample-service/context`

## 빠른 시작

```bash
cp .env.example .env
python3 scripts/specyn_tasks.py bootstrap
python3 scripts/specyn_tasks.py doctor
python3 scripts/specyn_tasks.py sample-flow
python3 scripts/specyn_tasks.py dev
python3 scripts/specyn_tasks.py sample-dev
```

- `python scripts/specyn_tasks.py dev` 는 Specyn 대시보드를 실행합니다.
- `python scripts/specyn_tasks.py sample-dev` 는 실제 sample-service 런타임을 실행합니다.

## sample-service 실행 흐름

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
```

실행 결과는 저장소 루트가 아니라 아래에 생성됩니다.

```text
projects/sample-service/frontend
projects/sample-service/backend
projects/sample-service/ai-server
projects/sample-service/docs
```

새 spec bundle 시작점은 `specs/templates/`, 실행 가능한 참고 spec는 `specs/projects/sample-service/` 를 사용합니다.

## 문서

- [docs/quickstart.md](docs/quickstart.md)
- [docs/playbook.md](docs/playbook.md)
- [docs/cli-run-reference.md](docs/cli-run-reference.md)
- [docs/sample-service-reference.md](docs/sample-service-reference.md)
- [docs/troubleshooting.md](docs/troubleshooting.md)
- [guide/local-development.md](guide/local-development.md)
- [specs/README.md](specs/README.md)
- [tools/README.md](tools/README.md)
