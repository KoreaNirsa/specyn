# Dashboard AI Server

Specyn 대시보드의 FastAPI 기반 AI 실행 서버입니다.

## 역할

- agent prompt 조합
- OpenAI Responses API 호출
- Codex 실행
- 선택형 RAG 검색
- 실행 안전장치 적용

## 기본 실행

대시보드 전체 스택을 띄우는 기본 경로:

```bash
python specyn.py up -d
```

AI server 만 호스트에서 직접 띄우려면:

```bash
python -m uvicorn app.main:app --app-dir dashboard/ai-server --host 0.0.0.0 --port 8100 --reload
```

또는 보조 헬퍼:

```bash
python scripts/specyn_tasks.py ai-server
```
