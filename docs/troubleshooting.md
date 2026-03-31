# Troubleshooting

## 대시보드가 안 뜰 때

- `python scripts/specyn_tasks.py dev` 로 실행했는지 확인합니다.
- Dashboard 포트는 `4173 / 8180 / 8100` 입니다.

## sample-service가 안 뜰 때

- `python scripts/specyn_tasks.py sample-dev` 로 실행했는지 확인합니다.
- sample-service 포트는 `5173 / 8080 / 8000` 입니다.

## run 결과가 루트에 생성될 때

최신 구조에서는 `python specyn.py run` 결과가 반드시 `projects/<project-id>/...` 아래로 생성되어야 합니다.

## sample-service 확인 URL

- `http://localhost:5173`
- `http://localhost:8080/api/v1/generated/sample-service/summary`
- `http://localhost:8000/generated/sample-service/context`
