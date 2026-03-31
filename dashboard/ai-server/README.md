# ai-server

FastAPI 기반 Specyn AI 실행 서버다.

## 역할
- Agent prompt 조합
- OpenAI Responses API 호출
- Codex CLI 실행
- optional LangChain 기반 RAG 검색
- prompt safety guardrail 적용

## 실행

#### Linux / macOS
```bash
make ai-server
```

#### Windows (PowerShell)
```powershell
python scripts/specyn_tasks.py ai-server
```

## 주요 엔드포인트
- `GET /health`
- `POST /v1/agents/execute`
- `POST /v1/rag/search`

## 구현 포인트
- agent 이름은 소문자/하이픈 기준으로 정규화한다.
- `API/BACKEND/FRONTEND/DBA/TEST/DOCS` 계열 agent는 필요 시 Codex를 실행한다.
- RAG 결과는 근거 자료이며 시스템 지시로 승격하지 않는다.
- 동일 Agent가 다시 실행되면 bounded feedback round로 간주하고 변경 근거/해결 상태를 분리한다.

## 생성 대상 FastAPI / LangChain 구조 규약

Specyn이 생성하는 FastAPI/LangChain 서비스는 `app/global / app/common / app/domain` 구조를 권장한다.
현재 ai-server 런타임은 프레임워크 호환성을 위해 기존 `api/core/models/services` 구조를 유지하지만, 사용자 프로젝트 산출물은 `docs/10-structure-conventions.md` 규약을 따르는 편이 안정적이다.
