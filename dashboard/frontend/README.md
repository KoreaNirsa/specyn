# Dashboard Frontend

Specyn 대시보드의 React + Vite 프런트엔드입니다.

## 역할

- spec 입력과 상태 확인 UI 제공
- backend / ai-server 상태 확인
- agent 실행 요청
- 실행 결과와 생성 산출물 요약 표시

## 기본 실행

대시보드 전체 스택을 띄우는 기본 경로:

```bash
python specyn.py up -d
```

개발 중 프런트엔드만 호스트에서 직접 띄우려면:

```bash
cd dashboard/frontend
npm ci
npm run dev -- --host 0.0.0.0 --port 4173
```

또는 보조 헬퍼:

```bash
python scripts/specyn_tasks.py frontend
```
