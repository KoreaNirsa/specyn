# tools

`tools/`는 Specyn CLI 구현체와 보조 유틸리티를 포함한다.

## 주요 기능
- spec 초기화
- spec validation
- `agent.md` 기반 agent flow 해석
- prompt 컴파일
- backend 호출 기반 실행
- backend 없이 로컬 시뮬레이션 실행
- 로컬 환경 점검

사용자 진입점은 루트의 `specyn.py`다. 내부 구현은 `tools/specyn.py`에 있다.

## 대표 명령어

#### Linux / macOS
```bash
python3 specyn.py doctor
python3 specyn.py init-spec --project-id sample-service --output-dir specs/projects/sample-service
python3 specyn.py validate --spec-dir specs/examples/todo-service
python3 specyn.py compile-prompts --spec-dir specs/examples/todo-service --workspace .workspace/todo-service
python3 specyn.py run --spec-dir specs/examples/todo-service --workspace .workspace/todo-service
```

#### Windows (PowerShell)
```powershell
python specyn.py doctor
python specyn.py init-spec --project-id sample-service --output-dir specs/projects/sample-service
python specyn.py validate --spec-dir specs/examples/todo-service
python specyn.py compile-prompts --spec-dir specs/examples/todo-service --workspace .workspace/todo-service
python specyn.py run --spec-dir specs/examples/todo-service --workspace .workspace/todo-service
```
