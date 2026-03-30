# frontend

React + Vite 기반 Specyn UI다.

## 역할
- core spec(product/api/test/review/agent) 입력/편집
- backend / ai-server health 확인
- spec 실행 요청
- 결과 요약 확인

## 실행

#### Linux / macOS
```bash
make frontend
```

#### Windows (PowerShell)
```powershell
python scripts/specyn_tasks.py frontend
```

직접 실행하려면:
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## 참고
현재 UI는 core spec 편집을 중심으로 제공한다.
고급 사용에서는 CLI와 저장소 내 spec 파일을 함께 사용해 agent flow를 세밀하게 조정하는 것을 권장한다.
