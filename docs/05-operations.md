# 05. Operations

## 운영 관점에서 가장 먼저 할 일

1. 기본 검증 경로가 깨지지 않는지 확인
2. `doctor`로 로컬 의존성 상태 점검
3. spec validation과 prompt compile을 먼저 통과
4. 전체 스택 실행은 그 다음

## 로컬 실행

### Linux / macOS
```bash
# 1) 준비
cp .env.example .env
make bootstrap

# 2) 환경 점검
make doctor

# 3) 실패 없는 기본 검증 흐름
make validate-spec
make compile-prompts
make run-sim
```

### Windows (PowerShell)
```powershell
# 1) 준비
Copy-Item .env.example .env
python scripts/specyn_tasks.py bootstrap

# 2) 환경 점검
python scripts/specyn_tasks.py doctor

# 3) 실패 없는 기본 검증 흐름
python scripts/specyn_tasks.py validate-spec
python scripts/specyn_tasks.py compile-prompts
python scripts/specyn_tasks.py run-sim
```

## 전체 스택 로컬 실행

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

## Docker 실행

```bash
docker compose -f docker-compose.local.yml up --build
```

## CLI 흐름

### Linux / macOS
```bash
python3 specyn.py validate --spec-dir specs/examples/todo-service
python3 specyn.py compile-prompts --spec-dir specs/examples/todo-service --output-dir .specyn/prompts/todo-service --workspace .workspace/todo-service
python3 specyn.py run --spec-dir specs/examples/todo-service --workspace .workspace/todo-service
```

### Windows (PowerShell)
```powershell
python specyn.py validate --spec-dir specs/examples/todo-service
python specyn.py compile-prompts --spec-dir specs/examples/todo-service --output-dir .specyn/prompts/todo-service --workspace .workspace/todo-service
python specyn.py run --spec-dir specs/examples/todo-service --workspace .workspace/todo-service
```

## 운영 확장 포인트

- branch-per-run
- workspace isolation
- queue 기반 비동기 실행
- artifact 저장소 연계
- prompt snapshot / execution trace 보관
- 향후 dashboard / timeline / agent audit 기능 연계
