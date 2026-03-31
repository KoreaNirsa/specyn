# Quickstart

## 1. 초기 준비

```bash
cp .env.example .env
python3 scripts/specyn_tasks.py bootstrap
python3 scripts/specyn_tasks.py doctor
```

## 2. sample-service spec 실행

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
```

## 3. 대시보드 실행

```bash
python3 scripts/specyn_tasks.py dev
```

- Dashboard Frontend: `http://localhost:4173`
- Dashboard Backend: `http://localhost:8180`
- Dashboard AI Server: `http://localhost:8100`

## 4. 실제 프로젝트 런타임 실행

```bash
python3 scripts/specyn_tasks.py sample-dev
```

- sample-service Frontend: `http://localhost:5173`
- sample-service Backend summary: `http://localhost:8080/api/v1/generated/sample-service/summary`
- sample-service AI Server context: `http://localhost:8000/generated/sample-service/context`

생성 결과는 `projects/sample-service/` 아래에 정리됩니다.

## 참고 명령

```bash
python specyn.py validate --spec-dir specs/projects/sample-service
python specyn.py compile-prompts --spec-dir specs/projects/sample-service --output-dir .specyn/prompts/sample-service --workspace .workspace/sample-service
python specyn.py run --spec-dir specs/projects/sample-service --project-id sample-service --workspace .workspace/sample-service
python scripts/specyn_tasks.py dev
python scripts/specyn_tasks.py sample-dev
```
