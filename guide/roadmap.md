# 🗺 장기 확장 로드맵

Specyn은 현재도 바로 실행해 볼 수 있지만, 구조적으로는 아래 방향까지 자연스럽게 확장할 수 있도록 설계되어 있습니다.

## 1. 표준화 로드맵

| 단계 | 목표 | 예시 결과 |
|---|---|---|
| Stage 1 | 실행 가능한 reference framework | sample-service, quickstart, sample-flow |
| Stage 2 | 팀 도입 가능한 운영 프레임워크 | multi-sample, stronger CI, release policy |
| Stage 3 | 확장 가능한 SDD platform | plugin/runtime integration, benchmark suite |
| Stage 4 | 사실상 표준에 가까운 생태계 | community samples, governance, ecosystem tooling |

## 2. 플랫폼 확장

| 방향 | 예시 |
|---|---|
| Backend 확장 | ECS/Fargate, EKS |
| AI Server 분리 | private service, dedicated worker |
| Artifact 저장소 | S3, object storage |
| Queue | SQS, Kafka, RabbitMQ |
| Secret 관리 | Vault, Secrets Manager, 사내 secret manager |

## 3. 온프레미스 확장

- 내부 VM 또는 K8s로 backend / ai-server 분리 배포
- 사내 Git / artifact 저장소 / secret manager 연계
- 폐쇄망용 모델 프록시 또는 사내 LLM 게이트웨이 연계

## 4. 관측성과 운영 품질 확장

- agent timeline
- prompt snapshot browser
- artifact catalog
- reviewer decision audit
- token / cost 집계
- telemetry / tracing / metrics
- benchmark dashboard

## 5. 실행 모델 확장

- queue 기반 비동기 실행기
- branch-per-run
- PR bot / GitHub App 연동
- spec drift 탐지 자동화
- self-hosted runner 전략
- Copilot/Codex/사내 실행기 어댑터

## 6. 오픈소스 성장 축

- reference sample 카탈로그
- good first issue / maintainer workflow
- release cadence와 changelog
- 공개 데모 영상/스크린샷
- adoption 사례와 benchmark 결과
