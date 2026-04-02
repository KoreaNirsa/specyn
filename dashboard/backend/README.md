# Dashboard Backend

Specyn 대시보드의 Spring Boot 백엔드입니다.

## 역할

- spec bundle 수신과 필수 검증
- `agent.md` 기반 실행 흐름 해석
- AI Server 호출
- 단계별 결과 집계와 API 제공

## 기본 실행

대시보드 전체 스택을 띄우는 기본 경로:

```bash
python specyn.py up -d
```

백엔드만 호스트에서 직접 띄우려면:

```bash
cd dashboard/backend
./gradlew bootRun
```

Windows:

```powershell
cd dashboard/backend
.\gradlew.bat bootRun
```

repo-local Gradle 준비가 필요하면 보조 헬퍼를 사용합니다.

```bash
python scripts/specyn_tasks.py bootstrap
python scripts/specyn_tasks.py backend
```
