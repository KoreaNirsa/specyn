# 트러블슈팅

## `setup` 은 되는데 `up -d` 가 실패함

대부분 Docker Desktop 이 설치만 되어 있고 실행 중이 아니거나, Docker engine 이 아직 준비되지 않은 경우입니다.

Windows 에서 자주 보이는 오류:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine
```

권장 순서:

```bash
python specyn.py setup
python specyn.py auth-status
python specyn.py doctor

# Docker Desktop 시작

python specyn.py up -d
```

## dashboard frontend 가 바로 종료됨

확인:

```bash
docker compose -f docker-compose.local.yml ps
docker compose -f docker-compose.local.yml logs --tail 200 dashboard-frontend
```

기대 URL:

- `http://localhost:4173`

## 인증은 했는데 요청이 동작하지 않음

확인:

```bash
python specyn.py auth-status
```

점검 항목:

- 선택한 인증 모드
- `openapi` 모드에서 `OPENAI_API_KEY` 가 설정되었는지
- Docker 기반 인증 재사용을 위해 Docker Desktop 이 실행 중인지

## 민감 파일이 노출됨

`.env` 나 인증 캐시가 노출되었다면:

1. 커밋, 업로드, 공유 위치에서 즉시 제거합니다.
2. 필요하면 `OPENAI_API_KEY` 를 교체합니다.
3. 로컬 상태를 다시 맞추려면 `python specyn.py setup` 을 재실행합니다.

## sample runtime 이 열리지 않음

확인:

```bash
python specyn.py sample-up -d
docker compose -f docker-compose.local.yml ps
```

기대 URL:

- `http://localhost:5173`
- `http://localhost:8080/api/v1/generated/sample-service/summary`
- `http://localhost:8000/generated/sample-service/context`
