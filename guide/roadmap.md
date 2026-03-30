# 🗺 장기 확장 로드맵

Specyn은 현재도 바로 실행해 볼 수 있지만, 구조적으로는 아래 방향까지 자연스럽게 확장할 수 있도록 설계되어 있습니다.

## 1. 플랫폼 확장

| 방향 | 예시 |
|---|---|
| Backend 확장 | ECS/Fargate, EKS |
| AI Server 분리 | private service, dedicated worker |
| Artifact 저장소 | S3, object storage |
| Queue | SQS, Kafka, RabbitMQ |
| Secret 관리 | Vault, Secrets Manager, 사내 secret manager |

## 2. 온프레미스 확장

- 내부 VM 또는 K8s로 backend / ai-server 분리 배포
- 사내 Git / artifact 저장소 / secret manager 연계
- 폐쇄망용 모델 프록시 또는 사내 LLM 게이트웨이 연계

## 3. 관측성과 운영 품질 확장

- agent timeline
- prompt snapshot browser
- artifact catalog
- reviewer decision audit
- token / cost 집계
- telemetry / tracing / metrics

## 4. 실행 모델 확장

- queue 기반 비동기 실행기
- branch-per-run
- PR bot / GitHub App 연동
- spec drift 탐지 자동화
- self-hosted runner 전략
