# 00. Quickstart

## 먼저 기억할 원칙

처음에는 전체 스택 기동보다 **실패 없는 기본 검증 경로**를 먼저 확인하는 것이 좋다.
Specyn의 첫 진입은 아래 순서를 권장한다.

## 1) 기본 검증 경로

### Linux / macOS
```bash
cp .env.example .env
make bootstrap
make doctor
make validate-spec
make compile-prompts
make run-sim
```

### Windows (PowerShell)
```powershell
Copy-Item .env.example .env
python scripts/specyn_tasks.py bootstrap
python scripts/specyn_tasks.py doctor
python scripts/specyn_tasks.py validate-spec
python scripts/specyn_tasks.py compile-prompts
python scripts/specyn_tasks.py run-sim
```

이 경로는 Docker, OpenAI API 키, 시스템 Gradle 없이도 먼저 확인할 수 있다.

## 2) 전체 스택 로컬 네이티브 실행

### Linux / macOS
```bash
make bootstrap
make doctor
make dev
```

### Windows (PowerShell)
```powershell
python scripts/specyn_tasks.py bootstrap
python scripts/specyn_tasks.py doctor
python scripts/specyn_tasks.py dev
```

`doctor` 출력에서 `gradle.available=true`이면 Backend까지 포함한 로컬 실행 준비가 된 상태다.

## 3) Docker Compose 실행

```bash
docker compose -f docker-compose.local.yml up --build
```

## 4) 새 spec bundle 만들기

### Linux / macOS
```bash
python3 specyn.py init-spec \
  --project-id sample-service \
  --output-dir specs/projects/sample-service
```

### Windows (PowerShell)
```powershell
python specyn.py init-spec `
  --project-id sample-service `
  --output-dir specs/projects/sample-service
```

## 5) 어떤 문서를 먼저 읽으면 좋은가

- 구조 이해: `docs/01-architecture.md`
- spec 작성: `docs/02-spec-driven-development.md`
- agent 구성: `docs/03-agent-flow.md`
- 고급 적용: `docs/08-playbooks.md`
- 에러 대응: `docs/09-troubleshooting.md`
